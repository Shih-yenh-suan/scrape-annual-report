# -*- encoding: utf-8 -*-
from config import *
import datetime


def get_json(page):
    # 构建参数
    DATA['page'] = page
    if page == 1:
        if 'from' in DATA:
            del DATA['from']  # 对于第一页，不需要 from 参数
    else:
        DATA['from'] = (page - 1) * 100  # 对于后续页码，需要有 from 参数指定开始位置
    # 构建完整的请求 URL，并比对
    request_url = f"{URL}?{requests.compat.urlencode(DATA)}"
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


开启补充下载 = 1
ROOT = "N:\Source_for_sale\美股年报"
FILE_DOWNLOADS = f'{ROOT}\downloaded_files.txt'
FILE_PATH = f"{ROOT}"
DATE_RANGE = create_date_intervals(10, "2024-01-01")

if __name__ == '__main__':

    for i, dateRages in enumerate(DATE_RANGE):
        page = 0
        if 'max_page' in globals():
            del globals()['max_page']

        DATA['startdt'] = dateRages.split("~")[0]
        DATA['enddt'] = dateRages.split("~")[1]
        while page < 100:
            page += 1
            if get_json(page) == False:
                break
        time.sleep(5)
        logging.info(f"第 {dateRages} 区间完成, {i}/{len(DATE_RANGE)}")
    logging.info("全部完成！！")
