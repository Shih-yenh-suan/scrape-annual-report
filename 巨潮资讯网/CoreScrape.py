# -*- encoding: utf-8 -*-
import pandas as pd
import requests
import re
import datetime
import random
import time
import os
import threading
from Config import *


LOCK = threading.Lock()
with open(STOP_WORDS_LIST, 'r', encoding='utf-8') as file:
    STOP_WORDS = [line.strip() for line in file if not line.startswith('#')]


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
    if secCode == None:
        secCode = i['orgId'][5:11]

    down_url = 'http://static.cninfo.com.cn/' + i['adjunctUrl']

    # # 对于标题中不包含关键词的报告，停止下载
    # if not any(re.search(k, title) for k in SEARCH_KEY_LIST):
    #     print(f'{secCode}_{seYear}_{secName}：\t不含关键词 ({title})')
    #     return

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
    with open(LOCK_FILE_PATH, 'r', encoding='utf-8', errors='ignore') as lock_file:
        downloaded_files = lock_file.readlines()
        # 如果文件中出现线程准备下载的文件，则跳过
        if f'{filename}\n' in downloaded_files:
            print(f'{secCode}-{seYear}-{secName}：\t已在其他线程完成下载')
            return

    # 检查报告是否已经记录，补充下载专用
    if 开启补充下载 == 1:
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
    pageNum = 0
    while True:
        should_continue = process_page_for_downloads(
            pageNum)
        if not should_continue:
            break
        if pageNum >= 500:
            break
        pageNum += 1
