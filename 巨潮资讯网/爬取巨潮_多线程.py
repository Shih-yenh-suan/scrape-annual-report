# -*- encoding: utf-8 -*-
from Config import *
from CoreScrape import *


DATA['column'] = 'third'
DATA["category"] = CATEGORY[cate_now]
# DATA['searchkey'] = "社会责任;ESG;环境责任"

# 线程锁
if not os.path.exists(LOCK_FILE_PATH):
    with open(LOCK_FILE_PATH, 'w') as file:
        pass  # Just create the file if it does not exist

df = pd.read_excel(DATE_START_END_SHEET)
date_list = df["DATE"].dt.strftime('%Y-%m-%d')
date_list = list(date_list)[::-1]
date_gap = 200

DATE_START = date_list[::date_gap]
DATE_END = date_list[date_gap-1::date_gap]

if __name__ == '__main__':

    for disclosure_year in range(2016, 2003, -1):
        YearStart = str(disclosure_year)

        # # 按板块循环
        # for j in range(0, len(PLATE)):
        #     DATA['PLATE'] = PLATE[j]
        #     print(f"当前板块：{DATA['PLATE']}")
        # 按行业循环
        # for k in range(len(TRADE)-1, 0, -1):
        #     DATA['TRADE'] = TRADE[k]
        #     print(f"当前行业：{DATA['TRADE']}")

        # for i in range(1, 13):
        # i = str(i).zfill(2)
        # for date in range(1, 32):
        #     date = str(date).zfill(2)
        for i in range(0, len(DATE_START)):
            seDate = f"{DATE_START[i]}~{DATE_END[i]}"
            # seDate = f"{YearStart}-{i}-{date}~{YearStart}-{i}-{date}"
            DATA['seDate'] = seDate
            print(f"当前爬取区间：{seDate}")
            CircleScrape()

        print(f'{disclosure_year} 年的年报已下载完毕.')
