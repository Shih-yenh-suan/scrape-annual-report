# -*- encoding: utf-8 -*-
import requests
import re
import datetime
import time
import os
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor
from Config import *


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
DATA = {
    'pageNum': '',
    'pageSize': 30,
    'column': '',
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
    # 向网站获取内容和总页数，必须分开获取，否则容易报错
    result = retry_on_failure(lambda:
                              requests.post(URL, data=DATA, headers=HEADERS).json()['announcements'])

    maxpage = retry_on_failure(lambda:
                               requests.post(URL, data=DATA, headers=HEADERS).json()['totalpages'])
    if result is None or pageNum > maxpage:
        print(f"第 {pageNum} 页已无内容或超出最大页数，退出")
        return False
    # 开启多线程处理
    print(f'正在处理第 {pageNum} 页，共 {maxpage} 页')
    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(process_announcements, result)
    return True


def process_announcements(i):
    """处理json文件"""
    # 处理标题
    title = i['announcementTitle']
    title = re.sub(r'(<em>|</em>|[\/:*?"<>| ])', '', title)

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
    secName = i['secName'] if i['secName'] is not None else 'None'
    secName = re.sub(r'\*ST', '＊ST', secName)
    secName = re.sub(r'(<em>|</em>|[\/:*?"<>| ])', '', secName)
    secName = re.sub(r'Ａ', 'A', secName)
    secName = re.sub(r'Ｂ', 'B', secName)
    secName = re.sub(r'em', '', secName)

    # 处理代码
    secCode = i['secCode']
    if secCode == None:
        secCode = i['orgId'][5:11]

    # 处理文件后缀
    file_type = 'html' if i['adjunctType'] == None else 'pdf'

    # 整合文件名
    fileShortName = f'{secCode}_{seYear}_{secName}'
    fileName = f'{secCode}_{seYear}_{secName}_{title}_{announcementTime}.{file_type}'

    # 获取下载链接
    downloadUrl = 'http://static.cninfo.com.cn/' + i['adjunctUrl']

    # 执行下载函数
    download_file(downloadUrl, title, fileShortName, fileName)


def download_file(downloadUrl, title, fileShortName, fileName):
    """判断，并分块下载文件"""

    # 对于标题中不包含关键词的报告，跳过下载
    if 开启包含关键词 == 1:
        if not any(re.search(k, title) for k in SEARCH_KEY_LIST[file_type]):
            print(f'{fileShortName}：\t不含关键词 ({title})')
            return

    # 对于标题包含停用词的报告，跳过下载
    if any(re.search(k, title) for k in STOP_WORDS):
        print(f'{fileShortName}：\t包括停用词 ({title})')
        return

    # 创建保存路径
    if not os.path.exists(SAVING_PATH):
        os.makedirs(SAVING_PATH)
    filePath = os.path.join(SAVING_PATH, fileName)

    # 对于已经下载的报告，跳过下载
    if os.path.exists(filePath):
        print(f'{fileShortName}：\t已存在，跳过下载')
        return

    # 对于已经存在记录的报告，跳过下载
    with open(LOCK_FILE_PATH, 'r', encoding='utf-8', errors='ignore') as lock_file:
        downloaded_files = lock_file.readlines()
        if f'{fileName}\n' in downloaded_files:
            print(f'{fileShortName}：\t已记录在文件中')
            return

    # 一切都符合要求，分块下载文件
    try:
        with requests.get(downloadUrl, stream=True) as r:
            r.raise_for_status()
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        tmp_file.write(chunk)
                temp_name = tmp_file.name
        shutil.move(temp_name, filePath)
        print(f'{fileShortName}：\t已下载到 {filePath}')
    except Exception as e:
        print(f'{fileShortName}下载失败:  {e}')


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
    pageNum = 0
    while True:
        should_continue = process_page_for_downloads(pageNum)
        if not should_continue:
            break
        if pageNum >= 500:
            break
        pageNum += 1


def create_date_intervals(interval, start_date="2000-01-01", end_date=None):
    # 将字符串日期转换为datetime对象
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    # 如果没有提供结束日期，则默认为今天
    if end_date is None:
        end = datetime.datetime.today()
    else:
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    # 初始化日期列表
    intervals = []
    # 当前开始日期
    current_start = start
    while current_start < end:
        # 计算当前结束日期
        current_end = current_start + datetime.timedelta(days=interval)
        # 如果当前结束日期超过了总结束日期，就将其设置为总结束日期
        if current_end > end:
            current_end = end
        # 将当前日期区间添加到列表
        intervals.append(
            f"{current_start.strftime('%Y-%m-%d')}~{current_end.strftime('%Y-%m-%d')}")
        # 更新下一个区间的开始日期
        current_start = current_end + datetime.timedelta(days=1)
    return intervals
