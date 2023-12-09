URL = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'
HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Length': '181',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Host': 'www.cninfo.com.cn',
    'Origin': 'http://www.cninfo.com.cn',
    'Referer': 'http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'}

DATE_START_END_SHEET = "D:\ZZZMydocument\Codes\scrape-annual-reports\巨潮资讯网\日期表.xlsx"
STOP_WORDS_LIST = "D:\ZZZMydocument\Codes\scrape-annual-reports\巨潮资讯网\停用词.txt"

"""表单数据字典"""
COLUMN = {
    "深沪京": "szse",
    "港股": "hke",
    "三板": "third",
    "基金": "fund",
    "债券": "bond",
    "监管": "regulator",
    "预披露": "pre_disclosure"
}
PLATE = ['sz', 'szmb', 'szcy', 'sh', 'shmb', 'shkcp', 'bj']
CATEGORY = {
    "A股年报": "category_ndbg_szsh",
    "A股半年报": "category_bndbg_szsh",
    "A股一季报": "category_yjdbg_szsh",
    "A股三季报": "category_sjdbg_szsh",
    "A股业绩报告": "category_yjygjxz_szsh",
    "A股社会责任报告": "",
    "三板年度报告": "category_dqgg"
}
TRADE = ['农、林、牧、渔业', '电力、热力、燃气及水生产和供应业', '交通运输、仓储和邮政业',
         '金融业', '科学研究和技术服务业', '教育', '综合', '采矿业', '建筑业', '住宿和餐饮业',
         '房地产业', '水利、环境和公共设施管理业', '卫生和社会工作', '制造业', '批发和零售业',
         '信息传输、软件和信息技术服务业', '租赁和商务服务业', '居民服务、修理和其他服务业', '文化、体育和娱乐业']

SEARCH_KEY_LIST = ['社会和', '社会及', '社会、', 'ESG', '社会、', '社会、',
                   '社会与', '社会责任', '社会企业责任', '社会暨', '社会治理',
                   '环境报告书', '环境责任', '环境及治理', '环境管理', '环境报告书',
                   '可持续发展']
SEARCH_KEYS = ';'.join(SEARCH_KEY_LIST)

DATA = {
    'pageNum': '',
    'pageSize': 30,
    'column': '',
    'tabName': 'fulltext',
    'PLATE': '',
    'stock': '',
    'searchkey': '',
    'secid': '',
    'category': '',
    'TRADE': '',
    'seDate': '',
    'sortName': '',
    'sortType': '',
    'isHLtitle': 'true'
}

cate_now = "A股年报"
SAVING_PATH = f'E:\Downloads\{cate_now}'
LOCK_FILE_PATH = f'E:\Downloads\{cate_now}\downloaded_files.txt'
RECORDS = f'E:\Downloads\{cate_now}\downloaded_id.txt'

开启补充下载 = 0
