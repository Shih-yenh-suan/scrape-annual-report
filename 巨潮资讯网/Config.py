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
TRADE = ['农、林、牧、渔业', '电力、热力、燃气及水生产和供应业', '交通运输、仓储和邮政业',
         '金融业', '科学研究和技术服务业', '教育', '综合', '采矿业', '建筑业', '住宿和餐饮业',
         '房地产业', '水利、环境和公共设施管理业', '卫生和社会工作', '制造业', '批发和零售业',
         '信息传输、软件和信息技术服务业', '租赁和商务服务业', '居民服务、修理和其他服务业', '文化、体育和娱乐业']
PLATE = ['sz', 'szmb', 'szcy', 'sh', 'shmb', 'shkcp', 'bj']
CATEGORY = {
    "A股年报": "category_ndbg_szsh",
    "A股半年报": "category_bndbg_szsh",
    "A股一季报": "category_yjdbg_szsh",
    "A股三季报": "category_sjdbg_szsh",
    "A股业绩报告": "category_yjygjxz_szsh",
    "三板年度报告": "category_dqgg"
}


STOP_WORDS = ['摘要', '英文', '回复', '细则', '基金', '已取消', '延迟', '提示', '意见'
              '季度', 'eport', '财务指标', '说明', '管理办法', '半年', '半<em>年',
              '制度', '变更', '表格', '设立', '规则', '签字页', '决议公告', '纲要',
              '鉴证', '内部控制', '审计', '审核', '债券', '自查', '声明', '整改', '回函',
              '更正前', '更正公告', '差错更正', '更新前', '修正公告', '修订公告',
              '更正披露', '更正事项', '专项活动', '方案', '研究报告', '检查', '核查',
              '补充资料', '补充披露', '补充公告', '补充说明', '补充报告', '的公告',
              '社会公众', '有限责任', '担保', '责任主体',
              '季度', '中期'
              ]  #
# SEARCH_KEY_LIST = "['環境、社會']"
# SEARCH_KEYS = ';'.join(SEARCH_KEY_LIST)
# 暂时没用上 = ['\;', '致.*?股东', '；', '\(2', '\(II', '刊发',
#          '通知', '回覆', '澄清', '函件', '公告',]
DATE_START_END_SHEET = "D:\ZZZMydocument\Codes\scrape-annual-reports\日期表.xlsx"

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
