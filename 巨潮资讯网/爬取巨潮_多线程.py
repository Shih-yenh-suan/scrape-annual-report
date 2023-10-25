# -*- encoding: utf-8 -*-
import requests
import re
import datetime
import random
import time
import os
import threading

# 线程锁
LOCK = threading.Lock()
LOCK_FILE_PATH = 'E:\Downloads\上市公司报告位置\downloaded_files.txt'
if not os.path.exists(LOCK_FILE_PATH):
    with open(LOCK_FILE_PATH, 'w') as file:
        pass  # Just create the file if it does not exist

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
              '半年', '半<em>年', '季度', 'eport', '财务指标', '说明', '管理办法',
              '制度', '变更', '表格', '设立', '规则', '签字页', '决议公告', '纲要',
              '鉴证', '内部控制', '审计', '审核', '债券', '自查', '声明', '整改', '回函',
              '更正前', '更正公告', '差错更正', '更新前', '修正公告', '修订公告',
              '更正披露', '更正事项', '专项活动', '方案', '研究报告', '检查', '核查',
              '补充资料', '补充披露', '补充公告', '补充说明', '补充报告', '的公告'
              ]
SEARCH_KEY_LIST = ['環境、社會']
SEARCH_KEYS = ';'.join(SEARCH_KEY_LIST)
暂时没用上 = ['\;', '致.*?股东', '；', '\(2', '\(II', '刊发',
         '通知', '回覆', '澄清', '函件', '公告',]
DATA = {
    'pageNum': '',
    'pageSize': 30,
    'column': 'szse',
    'tabName': 'fulltext',
    'PLATE': '',
    'stock': '',
    'searchkey': SEARCH_KEYS,
    'secid': '',
    'category': '',
    'TRADE': '',
    'seDate': '',
    'sortName': '',
    'sortType': '',
    'isHLtitle': 'true'
}


def process_page_for_downloads(pageNum):
    """处理指定页码的公告信息并下载相关文件"""
    DATA['pageNum'] = pageNum
    DATA['seDate'] = seDate

    result = retry_on_failure(lambda:
                              requests.post(URL, data=DATA, headers=HEADERS).json()['announcements'])

    maxpage = retry_on_failure(lambda:
                               requests.post(URL, data=DATA, headers=HEADERS).json()['totalpages'])

    if result is None:
        print(f"第 {pageNum} 页已无内容，退出")
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
    seYear = str(int(announcementTime[0:4])-1)

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

    # 对于标题中不包含关键词的报告，停止下载
    if not any(re.search(k, title) for k in SEARCH_KEY_LIST):
        print(f'{secCode}_{seYear}_{secName}：\t不含关键词 ({title})')
        return

    # 对于标题包含停用词的公告，跳过下载
    if any(re.search(k, title) for k in STOP_WORDS):
        print(f'{secCode}_{seYear}_{secName}：\t包括停用词 ({title})')
        return

    # 否则，执行公告标准化函数
    prepare_and_download_file(
        secCode, title, announcementTime, down_url, secName)


def prepare_and_download_file(secCode, title, announcementTime, down_url, secName):
    """下载公告，重命名"""
    seYear = str(int(announcementTime[0:4])-1)
    filename = f'{secCode}_{seYear}_{secName}_{title}_{announcementTime}.pdf'

    if not os.path.exists(SAVING_PATH):
        os.makedirs(SAVING_PATH)

    filepath = os.path.join(SAVING_PATH, filename)

    # 检查报告是否已经下载
    if os.path.exists(filepath):
        print(f'{secCode}-{seYear}-{secName}：\t已存在，跳过下载')
        return

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


TRADE = ['农、林、牧、渔业', '电力、热力、燃气及水生产和供应业', '交通运输、仓储和邮政业',
         '金融业', '科学研究和技术服务业', '教育', '综合', '采矿业', '建筑业', '住宿和餐饮业',
         '房地产业', '水利、环境和公共设施管理业', '卫生和社会工作', '制造业', '批发和零售业',
         '信息传输、软件和信息技术服务业', '租赁和商务服务业', '居民服务、修理和其他服务业', '文化、体育和娱乐业']
PLATE = ['sz', 'szmb', 'szcy', 'sh', 'shmb', 'shkcp', 'bj']
DATE_START = ["01-01", "04-01", "04-21", "04-26", "04-28", "05-01"]
DATE_END = ["03-31", "04-20", "04-25", "04-27", "04-30", "05-01"]
SAVING_PATH = f'E:\Downloads\上市公司报告位置\CSR报告'

if __name__ == '__main__':

    for disclosure_year in range(2022, 1999, -1):
        YearStart = str(disclosure_year + 1)

        # # 按板块循环
        # for j in range(0,len(PLATE)):
        #     DATA['PLATE'] = PLATE[j]

        #     # 按行业循环
        #     for k in range(0,len(TRADE)):
        #         DATA['TRADE'] = TRADE[k]

        for i in range(0, len(DATE_START)):
            seDate = f"{YearStart}-{DATE_START[i]}~{int(YearStart)+1}-{DATE_END[i]}"
            # seDate = f"{YearStart}-01-01~{YearStart}-12-31"
            print(f"当前爬取区间：{seDate}")
            pageNum = 1
            while True:
                should_continue = process_page_for_downloads(pageNum)
                if not should_continue:
                    break
                if pageNum >= 500:
                    break
                pageNum += 1

        print(f'{disclosure_year} 年的年报已下载完毕.')
