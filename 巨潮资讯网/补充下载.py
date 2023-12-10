# -*- encoding: utf-8 -*-
from Config import *
from CoreScrape import *


DATA['column'] = COLUMN['深沪京']
# DATA["category"] = CATEGORY[cate_now]
DATA['searchkey'] = "年度报告;年报"

# 线程锁
if not os.path.exists(LOCK_FILE_PATH):
    with open(LOCK_FILE_PATH, 'w') as file:
        pass  # Just create the file if it does not exist

df = pd.read_excel(DATE_START_END_SHEET)
date_list = df["DATE"].dt.strftime('%Y-%m-%d')
date_list = list(date_list)[6300:][::-1]
date_gap = 0

if date_gap == 0:
    DATE_START = DATE_END = date_list[::-1]
else:
    DATE_START = date_list[::date_gap]
    DATE_END = date_list[date_gap-1::date_gap]

if __name__ == '__main__':

    # 按年份循环
    # for disclosure_year in range(2001, 2023, 1):
    #     YearStart = str(disclosure_year)
    #     for date_range in range(0, len(DATE_START)):
    #       # seDate = f"{YearStart}-{i}-{date}~{YearStart}-{i}-{date}"
    #         seDate = f"{YearStart}-{DATE_START[date_range]}~{YearStart}-{DATE_END[date_range]}"
    # # 按板块循环
    # for plate in PLATE:
    #     DATA['plate'] = plate
    #     print(f"当前板块：{plate}")

    # # 按行业循环
    # for ind in TRADE:
    #     DATA['trade'] = ind
    #     print(f"当前行业：{ind}")

    for i, date_range in enumerate(range(0, len(DATE_START))):
        seDate = f"{DATE_START[date_range]}~{DATE_END[date_range]}"

        DATA['seDate'] = seDate
        print(f"当前爬取区间：{seDate}，为列表第 {i} 个")

        CircleScrape()
        if DATE_START[date_range + 1][4] != DATE_START[date_range][4]:
            print(f'{DATE_START[date_range][4]} 年的年报已下载完毕.')
