# -*- encoding: utf-8 -*-
from CoreScrape import URL, HEADERS, DATA, retry_on_failure
from Config import STOP_WORDS_DICT
import requests
import re
import datetime
import random
import os
'''
输入出错pdf所在的文件夹，以及输出重新下载的pdf所在的文件夹

对出错pdf的名称重新检索，即整合股票简称和标题，重新搜索
下载符合条件的文件，
并将其放入重新下载的文件夹
'''

STOP_WORDS = STOP_WORDS_DICT["normal_sw"]
DATA['column'] = 'szse'


def open_file_path(fileName, pages):
    '''获取出错的pdf文件名，提取有用信息'''
    # 打开PDF文件
    parts = fileName.replace(".pdf", "").split("_")
    if not len(parts) >= 4:
        return False

    stkcd = parts[0]  # 提取代码
    year = parts[1]  # 提取年份
    # tags = parts[2] # 提取标签（仅对社会责任报告）
    # shortname = parts[3] # 获取简称（仅对社会责任报告）
    # searchKey = parts[4] # 获取文件名，即搜索关键词（仅对社会责任报告）
    shortname = parts[2]  # 获取简称
    searchKey = parts[3]  # 获取文件名，即搜索关键词
    date = parts[-1]  # 获取日期
    fileInfo = (stkcd, year, shortname, searchKey, date)
    # fileInfo = [stkcd, year, shortname,searchKey, date, tags] # （仅对社会责任报告）

    (stkcd, year, shortname, searchKey, date) = fileInfo

    # 从日期提取区间
    seDateStr = datetime.datetime.strptime(date, "%Y-%m-%d")
    date_before = (seDateStr - datetime.timedelta(days=3)).strftime("%Y-%m-%d")
    date_after = (seDateStr + datetime.timedelta(days=3)).strftime("%Y-%m-%d")

    DATA['seDate'] = f'{date_before}~{date_after}'
    DATA['searchkey'] = searchKey
    DATA['pageNum'] = pages
    print(DATA)
    # 获取单页年报的数据，数据格式为json。获取json中的年报信息。
    result = retry_on_failure(lambda:
                              requests.post(URL, data=DATA, headers=HEADERS).json()['announcements'])

    maxpage = retry_on_failure(lambda:
                               requests.post(URL, data=DATA, headers=HEADERS).json()['totalpages'])
    if result is None or pages > maxpage:
        print(f"第 {pages} 页已无内容或超出最大页数，退出")
        return False

    # 否则，获取信息
    for i in result:
        # 处理标题，和检索内容不同的则跳过
        title = i['announcementTitle']
        title = re.sub(r'(<em>|</em>|[\/:*?"<>| ])', '', title)
        title = re.sub(r'\*', '＊', title)
        if not searchKey == title:
            print(f"{title}:标题不同，{searchKey} vs {title}")
            continue

        # 处理时间，和检索内容不同的则跳过
        announcementTime = i["announcementTime"]/1000
        announcementTime = datetime.datetime.utcfromtimestamp(
            announcementTime).strftime('%Y-%m-%d')
        if not date == announcementTime:
            print(f"{title}:日期不同，{date} vs {announcementTime}")
            continue

        # 处理代码，和检索内容不同的则跳过
        secCode = i['secCode']
        if secCode == None:
            secCode = i['orgId'][5:11]
        if not stkcd == secCode:
            print(f"{title}:代码不同，{stkcd} vs {secCode}")
            continue

        # 处理年份
        seYear = re.search(r'20\d{2}', title)
        if seYear is None:
            seYear = str(int(announcementTime[0:4])-1)
        else:
            seYear = seYear.group()

        # 处理简称
        secName = i['secName'] if i['secName'] is not None else 'None'
        secName = re.sub(r'\*', '＊', secName)
        secName = re.sub(r'(<em>|</em>|[\/:*?"<>| ])', '', secName)
        secName = re.sub(r'Ａ', 'A', secName)
        secName = re.sub(r'Ｂ', 'B', secName)
        secName = re.sub(r'em', '', secName)

        # 整合文件名
        # filename = f'{secCode}_{seYear}_{filesInfo[5]}_{secName}_{title}_{announcementTime}_{random.randint(1,4)}.pdf'
        filename = f'{secCode}_{seYear}_{secName}_{title}_{announcementTime}_{random.randint(1,4)}.pdf'

        # 保存文件
        filepath = os.path.join(saving_path, filename)
        downloadUrl = 'http://static.cninfo.com.cn/' + i['adjunctUrl']

        r = requests.get(downloadUrl)
        with open(filepath, 'wb') as f:
            f.write(r.content)
        print(f'{secCode}-{seYear}-{secName}-{title}：\t下载完毕')
        return True
    return True


folder_path = r'E:\[待整理]Source_for_sale\年报'
saving_path = r'E:\[待整理]Source_for_sale\年报'
files = [files for files in os.listdir(
    folder_path) if files.endswith('.pdf')]

if __name__ == '__main__':

    if not os.path.exists(saving_path):
        os.makedirs(saving_path)

    for fileName in files:
        print(f"正在处理 {fileName}")
        pages = 1
        while True:
            should_continue = open_file_path(fileName, pages)
            if not should_continue:
                break
            if pages >= 10:
                break
            pages += 1
