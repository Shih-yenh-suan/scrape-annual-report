# -*- encoding: utf-8 -*-
import html
import json
import pandas as pd
import requests
import re
import datetime
import random
import time
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from Config import *

LOCK = threading.Lock()

if not os.path.exists(LOCK_FILE_PATH):
    with open(LOCK_FILE_PATH, 'w') as file:
        pass

with open(STOP_WORDS_LIST, 'r', encoding='utf-8') as file:
    STOP_WORDS = [line.strip() for line in file if not line.startswith('#')]


def process_years(year):

    lang = "zh"
    if 下载英文版面报告 == 1:
        lang = "en"
    URL = f"https://www1.hkexnews.hk/search/titleSearchServlet.do?\
sortDir=0&sortByOptions=DateTime&category=0&market=SEHK&stockId=-1\
&documentType=-1&fromDate={year}0101&toDate={year}1231&title=&\
searchType=1&t1code=40000&t2Gcode=-2&t2code=40100&rowRange=3000&lang={lang}"
    """处理指定页码的公告信息并下载相关文件"""
    result = retry_on_failure(lambda:
                              requests.get(URL, headers=HEADERS)).json()["result"]

    result = json.loads(result)

    # Create a ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit tasks to the executor
        futures = [executor.submit(process_and_download, file, year)
                   for file in result]

        # Optionally, you can wait for all tasks to complete and handle their results
        for future in as_completed(futures):
            try:
                future.result()  # This will re-raise any exception raised in process_and_download
            except Exception as exc:
                pass


def process_and_download(file_dict, year):
    file_link, file_name, short_name, file_bytes = process_announcements(
        file_dict, year)
    prepare_and_download_file(file_link, file_name, short_name, file_bytes)


def process_announcements(file_dict, year):
    news_id = file_dict["NEWS_ID"]
    stock_name = file_dict["STOCK_NAME"].split("br", 1)[0]
    title = file_dict["TITLE"]
    title = re.sub(r'\n', '', title)
    title = re.sub(r'\r', '', title)
    title = re.sub(r'[\/:\*?"<>| ]', '', title)
    date = file_dict["DATE_TIME"][:10]
    date = re.sub(r'(/)', '-', date)
    file_link = "https://www1.hkexnews.hk" + file_dict["FILE_LINK"]
    stkcd = file_dict["STOCK_CODE"].split("br", 1)[0]
    file_type = file_dict["FILE_TYPE"]
    file_bytes = file_dict["FILE_INFO"]

    year_re = year
    sorted_mappings = sorted(string_to_year.items(),
                             key=lambda x: len(x[0]), reverse=False)

    for string, y in sorted_mappings:
        # 使用正则表达式查找所有匹配结果
        matches = re.findall(string, title)

        # 如果有匹配结果，则更新year_re为最后一个匹配结果对应的年份
        if matches:
            year_re = str(y)
    file_name = f'{stkcd}_{year_re}_{stock_name}_{title}_{date}.{file_type}'
    file_name = re.sub(r'[\/:\*?"<>| ]', '', file_name)

    short_name = f"{stkcd}_{year_re}"
    short_name = re.sub(r'[\/:\*?"<>| ]', '', short_name)
    # 对于标题包含停用词的公告，跳过下载
    if any(re.search(k, title) for k in STOP_WORDS):
        print(f'{short_name}：\t包括停用词 ({title})')
        return

    return file_link, file_name, short_name, file_bytes


def prepare_and_download_file(file_link, file_name, short_name, file_bytes):
    """下载文件"""

    if not os.path.exists(SAVING_PATH):
        os.makedirs(SAVING_PATH)

    file_path = os.path.join(SAVING_PATH, file_name)

    # 检查报告是否已经下载
    if os.path.exists(file_path):
        # print(f'{short_name}：\t已存在，跳过下载')
        return

    # 检查报告是否已经记录，补充下载专用
    if 开启补充下载 == 1:
        with open(RECORDS, 'r', encoding='utf-8', errors='ignore') as lock_file:
            downloaded_files = lock_file.readlines()
            # 如果文件中出现线程准备下载的文件，则跳过
            if f'{short_name}\n' in downloaded_files:
                print(f'{short_name}：\t已存在记录')
                return
            with open(RECORDS, 'a', encoding='utf-8', errors='ignore') as lock_file:
                lock_file.write(f'{short_name}\n')

    # 使用线程锁防止冲突
    with LOCK:
        with open(LOCK_FILE_PATH, 'r', encoding='utf-8', errors='ignore') as lock_file:
            downloaded_files = lock_file.readlines()
        # 如果文件中出现线程准备下载的文件，则跳过
        if f'{file_name}\n' in downloaded_files:
            print(f'{short_name}：\t已在其他线程完成下载')
            return
        # 对于正下载或已下载的文件，保存文件名。
        with open(LOCK_FILE_PATH, 'a', encoding='utf-8', errors='ignore') as lock_file:
            lock_file.write(f'{file_name}\n')

    # 执行下载函数
    download_file(file_link, file_path, short_name, file_bytes)


def download_file(file_link, file_path, short_name, file_bytes):
    """分块下载文件"""
    # 获取保存路径
    download_path = os.path.join(
        os.path.basename(
            os.path.dirname(file_path)), os.path.basename(file_path))
    print(f'{short_name}：\t正在下载，大小 {file_bytes}：{download_path}')

    with requests.get(file_link, stream=True) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


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


if __name__ == "__main__":
    for year in range(2007, 2024, 1):
        print("==" * 20 + f'开始处理 {year} 年公告' + "==" * 20)
        process_years(year)
