# -*- encoding: utf-8 -*-
from CoreScrape import *
from Config import *


DATA_PARAMS = {
    # 注意此表，从中获取需要的信息
    'column': [
        'szse',  # 0. 深沪京
        'hke',  # 1. 港股
        'third',  # 2. 三板
    ],
    'plate': [
        'sz',  # 深市
        'szmb',  # 深主板
        'szcy',  # 创业版
        'sh',  # 沪市
        'shmb',  # 沪主板
        'shkcp',  # 科创版
        'bj'  # 北交所
    ],
    'category': [
        'category_ndbg_szsh',  # 0. A股年度报告
        'category_bndbg_szsh',  # 1. A股半年报
        'category_yjdbg_szsh',  # 2. A股一季报
        'category_sjdbg_szsh',  # 3. A股三季报
        'category_yjygjxz_szsh',  # 4. A股业绩报告
        'category_dqgg'  # 5. 三板年度报告
    ],
    'trade': TRADE
}


interval = 31  # 起始日期和结束日期之间的间隔。
start_date = '2000-01-01'  # 起始日期。默认为2000-01-01
end_date = None  # 默认为今天

DATA['column'] = "szse"
DATA['category'] = 'category_ndbg_szsh'

if 开启包含关键词 == 1:
    DATA['searchkey'] = ";".join(SEARCH_KEY_LIST["年报"])


if __name__ == '__main__':
    DATA_RANGE = create_date_intervals(interval, start_date, end_date)

    DATA_RANGE = DATA_RANGE[::-1]  # 是否倒序

    for i, seDate in enumerate(DATA_RANGE):

        DATA['seDate'] = seDate
        print(f"当前爬取区间：{seDate}，为列表第 {i+1}/{len(DATA_RANGE)} 个")

        CircleScrape()
        if seDate[3] != seDate[14]:
            print(f'{seDate[:4]} 年的年报已下载完毕.')


# DATA = {
#     'column': '',
#     'tabName': 'fulltext',
#     'plate': '',
#     'stock': '',
#     'searchkey': '',
#     'secid': '',
#     'category': '',
#     'trade': '',
#     'seDate': '',
#     'sortName': '',
#     'sortType': '',
#     'isHLtitle': 'true'
# }
