import random

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
