#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-

"""
导入三个包：
tyc_login：登录模块；
tyc_urls_crawler：链接爬取模块；
tyc_singlepage_crawler：详细页爬取模块。
"""

from pprint import pprint

from tyc_spider import tyc_login
from tyc_spider import tyc_urls_crawler
from tyc_spider import tyc_singlepage_crawler


# 登录爬虫两个参数，电话号码跟密码
PHONE = 'phone'
PASSWORD = 'password'

# 关键词列表
KEYWORDS = ['航空仿真摄影']

# 状态列表
STATUS = ['在业', '存续']

# 登录
login_driver = tyc_login.TianyanchaLogin(PHONE, PASSWORD)

# 初始化 URL 爬虫
url_crawler = tyc_urls_crawler.TianyanchaUrlsCrawler(login_driver.driver, KEYWORDS, STATUS)

# 爬取返回 URL 列表
urls = url_crawler.crawl_urls()


# 初始化详细页爬虫
single_page_crawl = tyc_singlepage_crawler.TianyanchaSinglePageClawer(login_driver)

# 爬取信息，返回字典 result，自行对其处理
for link in urls:
   result = single_page_crawl.crawl_single_page(link)
   pprint(result)
