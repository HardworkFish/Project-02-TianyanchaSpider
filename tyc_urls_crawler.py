#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-

from random import randint
from time import sleep

from bs4 import BeautifulSoup


class TianyanchaUrlsCrawler:
    """
    爬详细页链接，传入登录后的 driver 以及关键字
    """
    def __init__(self, driver, keywords):
        """
        :param driver: selenium webdriver
        :param keywords: str
        """
        self.driver = driver
        self.keywords = keywords
        self.url_fmt = 'https://www.tianyancha.com/search/p{page_num}?{keyword}'
        self.url_list = []

    def crawl_urls(self):
        for keyword in self.keywords:
            pages = self.get_page_num(keyword)
            for page_num in range(1, int(pages)):
                url = self.url_fmt.format(page_num=page_num, keyword=keyword)
                self.driver.get(url)
                sleep(randint(300, 600)/100)

                soup = BeautifulSoup(self.driver.page_source, 'lxml')
                links = soup.findAll('a', class_="name ")
                for link in links:
                    self.url_list.append(link['href'])

        return self.url_list

    def get_page_num(self, keyword):
        """
        爬取页数
        :param keyword: str
        :return: int
        """
        url = self.url_fmt.format(page_num=1, keyword=keyword)

        try:
            self.driver.get(url)
            sleep(5)
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            num_end = soup.find('a', class_="num -end")
            return next(iter(num_end))[3:]

        except (AttributeError, TypeError):
            if self.driver:
                self.driver.close()
            raise
