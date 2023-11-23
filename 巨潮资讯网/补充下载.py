# -*- encoding: utf-8 -*-
import requests
import re
import datetime
import random
import time
import os
import threading

URL = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'
HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Length': '181',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Host': 'www.cninfo.com.cn',
    'Origin': 'http://www.cninfo.com.cn',
    'Referer': 'http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'}
STOP_WORDS = ['摘要', '英文', '回复', '细则', '基金', '已取消', '延迟', '提示', '意见'
              '季度', 'eport', '财务指标', '说明', '管理办法', '半年', '半<em>年',
              '制度', '变更', '表格', '设立', '规则', '签字页', '决议公告', '纲要',
              '鉴证', '内部控制', '审计', '审核', '债券', '自查', '声明', '整改', '回函',
              '更正前', '更正公告', '差错更正', '更新前', '修正公告', '修订公告',
              '更正披露', '更正事项', '专项活动', '方案', '研究报告', '检查', '核查',
              '补充资料', '补充披露', '补充公告', '补充说明', '补充报告', '的公告',
                            '社会公众', '有限责任', '担保', '责任主体'
              ]  # '半年', '半<em>年',
TRADE = ['农、林、牧、渔业', '电力、热力、燃气及水生产和供应业', '交通运输、仓储和邮政业',
         '金融业', '科学研究和技术服务业', '教育', '综合', '采矿业', '建筑业', '住宿和餐饮业',
         '房地产业', '水利、环境和公共设施管理业', '卫生和社会工作', '制造业', '批发和零售业',
         '信息传输、软件和信息技术服务业', '租赁和商务服务业', '居民服务、修理和其他服务业', '文化、体育和娱乐业']
PLATE = ['sz', 'szmb', 'szcy', 'sh', 'shmb', 'shkcp', 'bj']
CATEGORY = {
    "A股年报": "category_ndbg_szsh",
    "A股半年报": "category_bndbg_szsh",
    "A股一季报": "category_yjdbg_szsh",
    "A股三季报": "category_sjdbg_szsh",
    "A股业绩报告": "category_yjygjxz_szsh",
    "A股社会责任报告": ""
}

DATA = {
    'pageNum': '',
    'pageSize': 30,
    'column': 'szse',
    'tabName': 'fulltext',
    'plate': '',
    'stock': '',
    'searchkey': '',
    'secid': '',
    'category': '',
    'trade': '',
    'seDate': '',
    'sortName': '',
    'sortType': '',
    'isHLtitle': 'true'
}


def process_page_for_downloads(pageNum):
    """处理指定页码的公告信息并下载相关文件"""
    DATA['pageNum'] = pageNum

    result = retry_on_failure(lambda:
                              requests.post(URL, data=DATA, headers=HEADERS).json()['announcements'])

    maxpage = retry_on_failure(lambda:
                               requests.post(URL, data=DATA, headers=HEADERS).json()['totalpages'])

    if result is None:
        print(f"第 {pageNum} 页已无内容，退出")
        return False
    if pageNum > maxpage:
        print(f"第 {pageNum - 1} 页是最后一页，退出")
        return False

    print(f'正在处理第 {pageNum} 页，共 {maxpage} 页')

    # 创建一个线程列表
    threads = []

    for i in result:
        # 为每个公告启动一个线程
        thread = threading.Thread(target=process_announcements, args=(i,))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    return True


def process_announcements(i):
    """处理json文件"""
    # 处理标题
    title = i['announcementTitle']
    title = re.sub(r'(<em>|</em>|[\/:*?"<>| ])', '', title)
    title = re.sub(r'(Ａ)', 'A', title)

    # 处理时间
    announcementTime = i["announcementTime"]/1000
    announcementTime = datetime.datetime.utcfromtimestamp(
        announcementTime).strftime('%Y-%m-%d')

    # 处理年份
    seYear = re.search(r'20\d{2}', title)
    if seYear is None:
        seYear = str(int(announcementTime[0:4])-1)
    else:
        seYear = seYear.group()

    # 处理简称
    secName = i['secName']
    if secName == None:
        secName = 'None'
    secName = re.sub(r'\*ST', '＊ST', secName)
    secName = re.sub(r'[\/:\*?"<>| ]', '', secName)
    secName = re.sub(r'Ａ', 'A', secName)
    secName = re.sub(r'Ｂ', 'B', secName)
    secName = re.sub(r'em', '', secName)

    secCode = i['secCode']

    down_url = 'http://static.cninfo.com.cn/' + i['adjunctUrl']

    # 对于标题包含停用词的公告，跳过下载
    if any(re.search(k, title) for k in STOP_WORDS):
        print(f'{secCode}_{seYear}_{secName}：\t包括停用词 ({title})')
        return

    # 否则，执行公告标准化函数
    prepare_and_download_file(
        secCode, title, announcementTime, down_url, secName, seYear)


def prepare_and_download_file(secCode, title, announcementTime, down_url, secName, seYear):
    """下载公告，重命名"""
    filename = f'{secCode}_{seYear}_{secName}_{title}_{announcementTime}.pdf'

    if not os.path.exists(SAVING_PATH):
        os.makedirs(SAVING_PATH)

    filepath = os.path.join(SAVING_PATH, filename)

    # 检查报告是否已经下载
    if os.path.exists(filepath):
        print(f'{secCode}-{seYear}-{secName}：\t已存在，跳过下载')
        return
    # 检查报告是否已经记录
    with open(RECORDS, 'r', encoding='utf-8', errors='ignore') as lock_file:
        downloaded_files = lock_file.readlines()
        # 如果文件中出现线程准备下载的文件，则跳过
        if f'{secCode}_{seYear}\n' in downloaded_files:
            print(f'{secCode}-{seYear}-{secName}：\t已存在记录')
            return
        with open(RECORDS, 'a', encoding='utf-8', errors='ignore') as lock_file:
            lock_file.write(f'{secCode}_{seYear}\n')

    # 使用线程锁防止冲突
    with LOCK:
        with open(LOCK_FILE_PATH, 'r', encoding='utf-8', errors='ignore') as lock_file:
            downloaded_files = lock_file.readlines()
        # 如果文件中出现线程准备下载的文件，则跳过
        if f'{filename}\n' in downloaded_files:
            print(f'{secCode}-{seYear}-{secName}：\t已在其他线程完成下载')
            return
        # 对于正下载或已下载的文件，保存文件名。
        with open(LOCK_FILE_PATH, 'a', encoding='utf-8', errors='ignore') as lock_file:
            lock_file.write(f'{filename}\n')

    # 执行下载函数
    download_file(down_url, filepath, secCode, seYear, secName)


def download_file(down_url, filepath, secCode, seYear, secName):
    """分块下载文件"""
    with requests.get(down_url, stream=True) as r:
        r.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    # 获取保存路径
    result = os.path.join(
        os.path.basename(
            os.path.dirname(filepath)), os.path.basename(filepath))

    print(f'{secCode}_{seYear}_{secName}：\t已下载到 {result}')


def retry_on_failure(func):
    """对于请求失败的情况，暂停一段时间"""
    pause_time = 3
    try:
        result = func()
        return result
    except Exception as e:
        print(f'Error: {e}, 暂停 {pause_time} 秒')
        time.sleep(pause_time)
        return retry_on_failure(func)


def CircleScrape():
    pageNum = 1
    while True:
        should_continue = process_page_for_downloads(pageNum)
        if not should_continue:
            break
        if pageNum >= 500:
            break
        pageNum += 1


# 半年报
# DATE_START = ["01-01", "08-01", "08-11", "08-13", "08-15", "08-17",
#               "08-19", "08-21", "08-23", "08-25", "08-27", "08-29", "08-31", "09-02"]
# DATE_END = ["08-01", "08-10", "08-12", "08-14", "08-16", "08-18",
#             "08-20", "08-22", "08-24", "08-26", "08-28", "08-30", "09-01", "12-31"]
# 年报
DATE_START = ["01-01", "03-21", "04-02", "04-11", "04-21", "04-22", "04-23", "04-24",
              "04-25", "04-26", "04-27", "04-28", "04-29", "04-30", "05-01", "05-02"]
DATE_END = ["03-20", "04-01", "04-10", "04-20", "04-21", "04-22", "04-23", "04-24",
            "04-25", "04-26", "04-27", "04-28", "04-29", "04-30", "05-01", "12-31"]
# 一季报
# DATE_START = ["01-01", "04-01", "04-11", "04-21", "04-22", "04-23", "04-24",
#               "04-25", "04-26", "04-27", "04-28", "04-29", "04-30", "05-01", "05-02"]
# DATE_END = ["04-01", "04-10", "04-20", "04-21", "04-22", "04-23", "04-24",
#             "04-25", "04-26", "04-27", "04-28", "04-29", "04-30", "05-01", "12-31"]
# 三季报
# DATE_START = ["01-01", "10-01", "10-10", "10-13", "10-15", "10-17",
#               "10-19", "10-21", "10-23", "10-25", "10-27", "10-29", "10-31", "11-02"]
# DATE_END = ["10-01", "10-10", "10-12", "10-14", "10-16", "10-18",
#             "10-20", "10-22", "10-24", "10-26", "10-28", "10-30", "11-01", "12-31"]

cate_now = "A股社会责任报告"
SAVING_PATH = f'E:\Downloads\{cate_now}'
DATA["category"] = CATEGORY[cate_now]
RECORDS = f'E:\Downloads\{cate_now}\downloaded_id.txt'
LOCK_FILE_PATH = f'E:\Downloads\{cate_now}\downloaded_files.txt'
DATA['searchkey'] = "社会责任;ESG;环境责任"
# 线程锁
LOCK = threading.Lock()
if not os.path.exists(LOCK_FILE_PATH):
    with open(LOCK_FILE_PATH, 'w') as file:
        pass  # Just create the file if it does not exist

if __name__ == '__main__':

    # 按年份循环
    for disclosure_year in range(2001, 2023, 1):
        YearStart = str(disclosure_year)
        for date_range in range(0, len(DATE_START)):
            seDate = f"{YearStart}-{DATE_START[date_range]}~{YearStart}-{DATE_END[date_range]}"
            # seDate = f"{YearStart}-{i}-{date}~{YearStart}-{i}-{date}"
            DATA['seDate'] = seDate
            print(f"当前爬取区间：{seDate}")

            # # 按板块循环
            # for plate in PLATE:
            #     DATA['plate'] = plate
            #     print(f"当前板块：{plate}")

            #     # 按行业循环
            #     for ind in TRADE:
            #         DATA['trade'] = ind
            #         print(f"当前行业：{ind}")

            CircleScrape()

        print(f'{disclosure_year} 年的年报已下载完毕.')
