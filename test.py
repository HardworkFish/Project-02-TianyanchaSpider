#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-

import time

from selenium import webdriver
from bs4 import BeautifulSoup

import tyc_login
import tyc_urls_crawler
import tyc_singlepage_crawler


test = tyc_login.TianyanchaLogin('15602302053', 'MM112233')

# url = tyc_urls_crawler.TianyanchaUrlsCrawler(test.driver, ["腾讯"])

# url.crawl_urls()

single_page_crawl = tyc_singlepage_crawler.TianyanchaSinglePageClawer(test.driver)

single_page_crawl.crawl_single_page('https://www.tianyancha.com/company/407413576')


