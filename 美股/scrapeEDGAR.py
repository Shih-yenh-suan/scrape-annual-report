# -*- encoding: utf-8 -*-
import logging
import json
import requests
import re
import random
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import *

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s-%(levelname)s-%(message)s')

if not os.path.exists(RECORDS):
    with open(RECORDS, 'w') as file:
        pass


def get_json(page):
    # 导入记录文件
    with open(RECORDS, 'r', encoding='utf-8') as file:
        saved_urls = file.read().splitlines()
    # 构建参数

    DATA['page'] = page
    if page != 1:
        DATA['from'] = (page - 1) * 100  # 对于后续页码，需要有 from 参数指定开始位置

    # 构建完整的请求 URL，并比对
    request_url = f"{URL}?{requests.compat.urlencode(DATA)}"
    if request_url in saved_urls:
        logging.info(f"{page} 已存在，跳过此请求")
        return True

    # 请求网页，出错就反复请求
    try:
        logging.info(f"开始第 {page} 页, {request_url}")
        response = requests.get(URL, headers=HEADERS, params=DATA)
        json_original = json.loads(response.text)
        file_num = json_original['hits']['total']['value']
        max_page = file_num // 100 + 1
        logging.info(f"共 {max_page} 页， {file_num} 个文件")
        if page > max_page:
            logging.info(f"第 {page} 已无文件，当前区间完成")
            return False

        # 将成功的请求 URL 添加到文件中
        with open(RECORDS, 'a') as file:
            file.write(request_url + '\n')

    except Exception as e:
        logging.error(f"在处理 JSON 数据时出现错误: {e}")
        return True

    cop_info_full = json_original['hits']['hits']
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_cop_info = {executor.submit(
            process_cop_info, c): c for c in cop_info_full}

        for future in as_completed(future_to_cop_info):
            future.result()

    return True


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
        # logging.info(f'{File_Info}：已存在，跳过下载')
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
    time.sleep(random.uniform(1, 3))


def retry_on_failure(func):
    """对于请求失败的情况，暂停一段时间"""
    pause_time = 2
    retries = 0
    max_retries = 5
    while retries < max_retries:
        try:
            result = func()
            return result
        except Exception as e:
            logging.error(f'Retry {retries + 1}/{max_retries} for error: {e}')
            time.sleep(pause_time)
            retries += 1
    raise Exception(f"Failed after {max_retries} attempts")


if __name__ == '__main__':
    for year in range(2023, 2000, -1):
        page = 1
        DATA['startdt'] = f'{year}-01-01'
        DATA['enddt'] = f'{year}-12-31'
        while True:
            if get_json(page) == False:
                break
            page += 1
        logging.info("==" * 20 + f"{year} 已完成" + "==" * 20)
