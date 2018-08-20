#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-

import tyc_login
import tyc_urls_crawler
import tyc_singlepage_crawler


test = tyc_login.TianyanchaLogin('15663073264', 'mm112233')

url = tyc_urls_crawler.TianyanchaUrlsCrawler(test.driver, ["地理"])

urls = url.crawl_urls()

single_page_crawl = tyc_singlepage_crawler.TianyanchaSinglePageClawer(test.driver)

for link in urls:
    single_page_crawl.crawl_single_page(link)


