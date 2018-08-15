#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-

from time import sleep

from bs4 import BeautifulSoup


class TianyanchaUrlsCrawler:

    def __init__(self, driver, keywords):
        self.driver = driver
        self.keywords = keywords
        self.url_fmt = 'https://www.tianyancha.com/search/p{page_num}?{keyword}'

    def crawl_urls(self):
        url_list = []

        for keyword in self.keywords:
            pages = self.get_page_num(keyword)
            for page_num in range(1, int(pages)):
                url = self.url_fmt.format(page_num=page_num, keyword=keyword)
                print(url)
                self.driver.get(url)
                sleep(3)
                soup = BeautifulSoup(self.driver.page_source, 'lxml')
                links = soup.findAll('a', class_="name ")
                print(links)

    def get_page_num(self, keyword):
        url = self.url_fmt.format(page_num=1, keyword=keyword)

        try:
            self.driver.get(url)
            sleep(5)
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            num_end = soup.find('a', class_="num -end")
            return next(iter(num_end))[3:]

        except:
            if self.driver:
                self.driver.close()
            raise
