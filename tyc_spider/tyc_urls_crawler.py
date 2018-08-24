#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-

from random import randint
from time import sleep

from bs4 import BeautifulSoup


class TianyanchaUrlsCrawler:
    """
    爬详细页链接，传入登录后的 driver 以及关键字
    """
    def __init__(self, driver, keywords, status=None):
        """
        :param driver: selenium webdriver
        :param keywords: str
        """
        self.driver = driver
        self.keywords = keywords
        self.status = []
        if '在业' in status:
            self.status.append('1')
        if '存续' in status:
            self.status.append('2')
        if '吊销' in status:
            self.status.append('3')
        if '注销' in status:
            self.status.append('4')
        if '迁出' in status:
            self.status.append('5')
        if not status:
            self.status = ['1', '2', '3', '4', '5']
        print(self.status)
        self.url_fmt = 'https://www.tianyancha.com/search/os{status}/p{page_num}?key={keyword}&searchType=company'
        self.url_list = []

    def crawl_urls(self):
        for keyword in self.keywords:
            for status in self.status:
                pages = self.get_page_num(keyword, status)
                for page_num in range(1, int(pages)+1):
                    url = self.url_fmt.format(page_num=page_num, keyword=keyword, status=status)
                    self.driver.get(url)
                    sleep(randint(300, 600)/100)

                    soup = BeautifulSoup(self.driver.page_source, 'lxml')
                    links = soup.findAll('a', class_="name ")
                    print(keyword, page_num)
                    for link in links:
                        yield link['href']

    def get_page_num(self, keyword, status):
        """
        爬取页数
        :param keyword: str
        :return: int
        """
        url = self.url_fmt.format(page_num=1, keyword=keyword, status=status)

        try:
            self.driver.get(url)
            sleep(5)
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            page_ul = soup.find('ul', class_="pagination")
            page_links = page_ul.findAll('a')
            return page_links[-2].getText().lstrip('.')

        except (AttributeError, TypeError):
            if self.driver:
                self.driver.close()
            raise
