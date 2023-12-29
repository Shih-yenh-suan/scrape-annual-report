# -*- encoding: utf-8 -*-
from config import *


def get_json(page):
    # 导入记录文件
    with open(RECORDS, 'r', encoding='utf-8') as file:
        saved_urls = file.read().splitlines()
    # 构建参数
    DATA['page'] = page
    if page == 1:
        if 'from' in DATA:
            del DATA['from']  # 对于第一页，不需要 from 参数
    else:
        DATA['from'] = (page - 1) * 100  # 对于后续页码，需要有 from 参数指定开始位置
    # 构建完整的请求 URL，并比对
    request_url = f"{URL}?{requests.compat.urlencode(DATA)}"
    if (request_url in saved_urls) and (page != 1):
        # 如果当前请求url已经存在，则直接跳过，对于第一页永远需要发请求，因为需要获取最大页
        logging.info(f"{page} 已存在，跳过此请求")
        return True
    # 请求网页
    try:
        cop_info_full = retry_on_failure(lambda: json.loads(requests.get(
            URL, headers=HEADERS, params=DATA).text)['hits']['hits'])
        # 如果是第一页，或者总页数不存在，则执行请求以获取总页数
        if page == 1 or 'max_page' not in globals():
            file_num = retry_on_failure(lambda: json.loads(requests.get(URL, headers=HEADERS, params=DATA).text)[
                'hits']['total']['value'])
            global max_page  # 最大页数需要持续存储
            max_page = file_num // 100 + 1
            logging.info(f"共 {max_page} 页， {file_num} 个文件")

        # 如果当前页码超过了最大页码，则结束
        if page > max_page:
            logging.info(f"第 {page} 页超过最大页数，当前区间完成")
            return False
        # 一切正常时，执行爬取程序，并记录url
        logging.info(f"开始第 {page} 页, {request_url}")
        with open(RECORDS, 'a') as file:
            file.write(request_url + '\n')
    except Exception as e:
        logging.error(f" {page} 出错, {request_url}")
        time.sleep(5)
        return True
    # 通过try-except后，执行爬取程序
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_cop_info = {executor.submit(
            process_cop_info, c): c for c in cop_info_full}
        for future in as_completed(future_to_cop_info):
            future.result()

    return True


if __name__ == '__main__':
    for year in range(2009, 2000, -1):
        page = 0
        if 'max_page' in globals():
            del globals()['max_page']

        DATA['startdt'] = f'{year}-01-01'
        DATA['enddt'] = f'{year}-12-31'
        while page < 100:
            page += 1
            if get_json(page) == False:
                break
        time.sleep(5)
        logging.info("==" * 20 + f"{year} 已完成" + "==" * 20)
