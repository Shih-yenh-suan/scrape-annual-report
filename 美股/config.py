import random
import logging
import json
import requests
import re
import random
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


def process_cop_info(cop_info):
    Cop_Html, File_Name, File_Info = get_copHtml_and_fileName(cop_info)
    get_html_content(Cop_Html, File_Name, File_Info)


def get_copHtml_and_fileName(cop_info):
    # 提取网页HTML
    # 提取网页中的id，冒号之前的-要去除，冒号改/
    cop_id = cop_info["_id"]
    cop_id_1 = cop_id.split(":")[0]
    cop_id_1 = re.sub(r'-', '', cop_id_1)
    cop_id_2 = cop_id.split(":")[1]
    cop_id = f'{cop_id_1}/{cop_id_2}'
    # 提取网页中的cik
    ciks = cop_info['_source']['ciks'][0]
    # 拼成html
    Cop_Html = f'https://www.sec.gov/Archives/edgar/data/{ciks}/{cop_id}'

    # 提取文件名字，cik_会计期末_简称_企业名称_10-K_发布日期
    # 会计期末
    period_ending = cop_info['_source']['period_ending']
    # 提取企业全称、简称
    display_names = cop_info['_source']['display_names'][0]
    full_name_match = re.match(r"([^(]+)", display_names)
    full_name = full_name_match.group(1).strip() if full_name_match else None
    short_name_match = re.match(r"[^\(]+\((.*?)\).*CIK.*", display_names)
    short_name = short_name_match.group(1).split(
        ",")[0] if short_name_match else None
    # rootform获取是10-K还是20-F
    file_form = cop_info['_source']['file_type']
    # 获取发布日期
    file_date = cop_info['_source']['file_date']
    # 拼成文件名字
    File_Name = f"{ciks[3:]}_{period_ending}_{short_name}_{full_name}_{file_form}_{file_date}"
    File_Name = re.sub(r'[\\\/:\*?"<>|]', '', File_Name)
    # 拼成文件信息
    File_Info = f"{ciks[3:]}_{period_ending}"

    return Cop_Html, File_Name, File_Info


def get_html_content(Cop_Html, File_Name, File_Info):
    # 创建输出文件
    if not os.path.exists(FILE_PATH):
        os.makedirs(FILE_PATH)
    output_file_path = os.path.join(FILE_PATH, f'{File_Name}.html')
    if os.path.exists(output_file_path):
        logging.info(f'{File_Info}：已存在，跳过下载')
        return
    # 获取HTML内容f
    try:
        response = retry_on_failure(lambda:
                                    requests.get(Cop_Html, headers=HEADERS))
    except Exception as e:
        logging.error(f"在获取{Cop_Html}内容时出现错误: {e}")
        return
    html_text = response.text
    # 保存到html文件
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(html_text)
    # 打印File_Info信息
    logging.info(f"{File_Info}, {Cop_Html}")
    # 随机停止。SEC网站最大流量为1秒请求10次。
    time.sleep(random.uniform(1.5, 3.5))


def retry_on_failure(func):
    """对于请求失败的情况，暂停一段时间"""
    pause_time = 5
    retries = 0
    max_retries = 5
    while retries < max_retries:
        try:
            return func()
        except Exception as e:
            retries += 1
            logging.error(f'Retry {retries}/{max_retries} for error: {e}')
            time.sleep(pause_time * retries)

    raise Exception(f"Failed after {max_retries} attempts")


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s-%(levelname)s-%(message)s')


# 定义User-Agent列表
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Thunder Client (https://www.thunderclient.com)",
    # 更多User-Agent
]

# 你可以在需要的时候调用headers
# 每次调用时，User-Agent将从列表中随机选择
HEADERS = {
    "Accept": "*/*",
    "User-Agent": random.choice(user_agents)
}

DATA = {
    'dateRange': 'custom',
    'category': 'custom',
    'startdt': '',
    'enddt': '',
    'forms': '10-K,20-F',
    'page': '',
}

URL = "https://efts.sec.gov/LATEST/search-index"

FILE_PATH = "E:\Downloads\美股报告"
"""
参数：传入json: hits, hits为字符串，对于每个元素，_id中去除-，冒号改成/，形成两位网页标签ids。
在_source中查找ciks的第一个元素，组成变量cik
网页： https://www.sec.gov/Archives/edgar/data/cik/ids

"""
开启补充下载 = 1
RECORDS = f'{FILE_PATH}\RECORDS.txt'

if not os.path.exists(RECORDS):
    with open(RECORDS, 'w') as file:
        pass
