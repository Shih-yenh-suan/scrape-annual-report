import os
import pandas as pd
import re
import requests
import time
import threading
from urllib.parse import urlparse, parse_qs

HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7,en-GB;q=0.6,en-US;q=0.5',
    'Origin': 'https://www.nasdaq.com',
    'Referer': 'https://www.nasdaq.com/',
    'Sec-Ch-Ua': '"Chromium";v="118", "Microsoft Edge";v="118", "Not=A?Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
}

saving_path = r"E:\Downloads\美股报告"
if not os.path.exists(saving_path):
    os.makedirs(saving_path)

csv_path = r"scrape-annual-reports\美股\nasdaq_screener.csv"

symbol_list = list(pd.read_csv(csv_path)['Symbol'])
symbol_list = [str(s) for s in symbol_list]
symbol_list = [str.replace(s, '/', '-') for s in symbol_list]
symbol_list.sort()
print_lock = threading.Lock()


def download_url(symbol, year):

    url = f'https://api.nasdaq.com/api/company/{symbol}/sec-filings?limit=14&sortColumn=filed&sortOrder=desc&FormGroup=Annual%20Reports&Year={year}&IsQuoteMedia=true'

    while True:
        try:
            req_json = retry_on_failure(
                lambda: requests.get(url=url, headers=HEADERS)).json()
            break  # 如果成功获取JSON数据，则跳出循环
        except Exception as e:
            print(f"JSON解析错误: {e}, 等待 5 秒后重试")
            time.sleep(5)  # 等待5秒后重试

    try:
        pdfLink = req_json['data']["rows"]["formType" ==
                                           "10-K"]["view"]["pdfLink"]
        download_pdf(pdfLink, year)
    except IndexError:
        with print_lock:  # 使用线程锁
            print(f"{symbol} 第 {year} 年的数据不存在，继续")


def download_pdf(pdfLink, year):
    year = str(year - 1)

    # 从pdfLink中获取信息，组成文件名和路径
    parsed_url = urlparse(pdfLink)
    query_params = parse_qs(parsed_url.query)  # 提取参数为字典

    symbol = query_params['symbol'][0]  # 代码
    companyName = query_params['companyName'][0]  # 名称
    formDescription = query_params['formDescription'][0]  # 文件名
    dateFiled = query_params['dateFiled'][0]  # 日期
    filename = [symbol, year, companyName,
                formDescription, dateFiled, '.pdf']  # 整合的名字
    filename = "_".join(filename)  # 按照下划线整合
    filename = re.sub(r'[\/:*?"<>|]', '', filename)  # 去除非法字符
    filepath = os.path.join(saving_path, filename)  # 文件路径

    # Check if a file with the same symbol and year already exists, and if so, skip the download
    symbol_year_identifier = f"{symbol}_{year}"
    existing_files = [f for f in os.listdir(
        saving_path) if symbol_year_identifier in f]

    if existing_files:
        with print_lock:  # 使用线程锁
            print(f'{symbol} 第 {year} 年的数据已存在，跳过下载')
        return

    r = retry_on_failure(lambda:
                         requests.get(pdfLink, headers=HEADERS))
    with open(filepath, 'wb') as f:
        f.write(r.content)
    with print_lock:  # 使用线程锁
        print(f"{symbol} 第 {year} 年的数据已下载")


def retry_on_failure(func):
    try:
        result = func()
        return result
    except Exception as e:
        print(f'Error: {e}, 暂停 3 秒')
        time.sleep(3)
        return retry_on_failure(func)

# if __name__ == '__main__':

#     for s in symbol_list:
#         print(f'{s} 的报告开始下载')
#         for year in range(1994, 2023):
#             download_url(s, year)


# 主函数
if __name__ == '__main__':

    i = 0  # 可自定义开始行数
    for s in symbol_list[i:]:
        print(f"当前爬取：{i}")
        i += 1
        with print_lock:  # 使用线程锁
            print(f'{s} 的报告开始下载')

        threads = []

        # 为每个年份创建线程
        for year in range(1994, 2023):
            t = threading.Thread(target=download_url, args=(s, year))
            threads.append(t)
            t.start()

        # 等待所有线程完成
        for t in threads:
            t.join()
