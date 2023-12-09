# -*- encoding: utf-8 -*-
import requests
import re
import datetime
import random
import time
import os
import threading
'''
输入出错pdf所在的文件夹，以及输出重新下载的pdf所在的文件夹

对出错pdf的名称重新检索，即整合股票简称和标题，重新搜索
下载符合条件的文件，
并将其放入重新下载的文件夹
'''


LOCK = threading.Lock()
LOCK_FILE_PATH = 'downloaded_files.txt'
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
    'X-Requested-With': 'XMLHttpRequest'
}
STOP_WORDS = ['摘要', '英文', '回复', '细则', '基金', '已取消', '延迟', '提示', '意见'
              '季度', 'eport', '财务指标', '说明', '管理办法',
              '制度', '变更', '表格', '设立', '规则', '签字页', '决议公告', '纲要',
              '鉴证', '内部控制', '审计', '审核', '债券', '自查', '声明', '整改', '回函',
              '更正前', '更正公告', '差错更正', '更新前', '修正公告', '修订公告',
              '更正披露', '更正事项', '专项活动', '方案', '研究报告', '检查', '核查',
              '补充资料', '补充披露', '补充公告', '补充说明', '补充报告', '的公告'
              ]  # '半年', '半<em>年',
# ['\;', '致.*?股东', '；', '\(2', '\(II', '刊发','通知', '回覆', '澄清', '函件', '公告',]

data = {'pageNum': 1,
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
        'isHLtitle': 'true'}


def open_file_path(folder_path):
    '''获取出错的pdf文件名，提取有用信息'''
    # 打开PDF文件
    filesInfo = []
    for filename in os.listdir(folder_path):
        parts = filename.replace(".pdf", "").split("_")
        if len(parts) >= 4:
            stkcd = parts[0]  # 提取代码
            year = parts[1]  # 提取年份
            # tags = parts[2] # 提取标签（仅对社会责任报告）
            # shortname = parts[3] # 获取简称（仅对社会责任报告）
            # searchKey = parts[4] # 获取文件名，即搜索关键词（仅对社会责任报告）
            shortname = parts[2]  # 获取简称
            searchKey = parts[3]  # 获取文件名，即搜索关键词
            date = parts[-1]  # 获取日期
            fileInfo = [stkcd, year, shortname, searchKey, date]
            # fileInfo = [stkcd, year, shortname,searchKey, date, tags] # （仅对社会责任报告）
            filesInfo.append(fileInfo)

    return filesInfo


def retry_on_failure(func):
    '''当爬取失败时，暂停重试'''
    try:
        result = func()
        return result
    except Exception as e:
        print(f'错误: {e}, 暂停 3 秒')
        time.sleep(3)
        return retry_on_failure(func)


def get_and_download_pdf_file(filesInfo):
    '''获取链接并下载文件'''

    # 获取单页年报的数据，数据格式为json。获取json中的年报信息。
    result = retry_on_failure(
        lambda: requests.post(
            URL, data=data, headers=HEADERS).json()['announcements'])

    # 如果当前页面无内容，退出
    if result is None:
        print(f"未检索到内容，退出")
        return False

    # 否则，获取信息
    for i in result:

        # 对毫秒记录的发布日期进行标准化
        announcementTime = i["announcementTime"]
        announcementTime = announcementTime/1000
        announcementTime = datetime.datetime.utcfromtimestamp(
            announcementTime).strftime('%Y-%m-%d')

        seYear = str(int(announcementTime[0:4])-1)  # 从发布日期提取报告年份，但可能不准
        title = i['announcementTitle']  # 提取标题
        # 为了确保打印时好看，还是现在这里就对title标准化
        title = re.sub(r'(<em>|</em>|[\/:*?"<>| ])', '', title)
        title = re.sub(r'(Ａ)', 'A', title)

        secName = i['secName']  # 提取简称
        secCode = i['secCode']  # 提取代码
        down_url = 'http://static.cninfo.com.cn/' + \
            i['adjunctUrl']  # 提取下载链接并合并

        # 跳过包含停用词的
        if any(re.search(k, title) for k in STOP_WORDS):
            print(f'{title}：不满足要求，跳过')
            continue

        # 跳过股票代码不对的。
        if not any(re.search(k, i['secCode']) for k in filesInfo[0]):
            print(f'{title}：不满足要求，跳过')
            continue

        # 整合文件名
        # filename = f'{secCode}_{seYear}_{filesInfo[5]}_{secName}_{title}_{announcementTime}_{random.randint(1,4)}.pdf'
        filename = f'{secCode}_{seYear}_{secName}_{title}_{announcementTime}_{random.randint(1,4)}.pdf'

        # 将全角A转成半角，去掉搜索时的html痕迹，去掉无法被保存的字符。
        filename = re.sub(r'Ａ', 'A', filename)
        filename = re.sub(r'(<em>|</em>|[\/:?"<>| ])', '', filename)
        filename = re.sub(r'\*', '＊', filename)

        # 保存文件
        filepath = os.path.join(saving_path, filename)

        if os.path.exists(filepath):  # 检查文件是否存在
            print(f'{title}：\t已存在，跳过下载')

        r = requests.get(down_url)
        with open(filepath, 'wb') as f:
            f.write(r.content)
        print(f'{secCode}-{seYear}-{secName}-{title}：\t下载完毕')


if __name__ == '__main__':

    folder_path = ''
    saving_path = ''

    if not os.path.exists(saving_path):
        os.makedirs(saving_path)

    filesInfo = open_file_path(folder_path)

    for i in range(0, len(filesInfo)):

        data['searchkey'] = filesInfo[i][2] + filesInfo[i][3]
        print(data['searchkey'])
        get_and_download_pdf_file(filesInfo[i])
