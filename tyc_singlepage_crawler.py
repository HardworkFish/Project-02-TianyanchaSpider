#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-

import re

from bs4 import BeautifulSoup


class TianyanchaSinglePageClawer:
    """
    详细页爬虫
    """
    def __init__(self, driver):
        self.driver = driver

    def crawl_single_page(self, url):
        """
        :param url: str
        :return:
        """
        result = {}

        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, "lxml")

        certificates_pages_num = get_page_num(soup, 'certificate')
        bits_pages_num = get_page_num(soup, 'bid')
        patents_pages_num = get_page_num(soup, 'patent')
        copyrights_pages_num = get_page_num(soup, 'copyright')


def get_page_num(soup, data_type):
    """
    按类别获取页数
    :param soup: BeautifulSoup
    :param data_type: str
    :return: int
    """
    try:
        ul = soup.find('ul', {'change-type': re.compile(data_type)})
        pages = ul.find_all('li')
        if pages == 1:
            return 1
        else:
            return int(pages[-2].get_text().lstrip('.'))
    except AttributeError:
        return 1