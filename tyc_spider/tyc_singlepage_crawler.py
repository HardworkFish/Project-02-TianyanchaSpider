#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-

from pprint import pprint
from random import randint
import re
from time import sleep

from bs4 import BeautifulSoup


class TianyanchaSinglePageClawer:
    """
    详细页爬虫
    """
    def __init__(self, loginer):
        self.loginer = loginer
        self.driver = self.loginer.driver

    def crawl_single_page(self, url):
        """
        :param url: str
        :return: dict
        """

        result = {'url': url, 'company_id': url.split('/')[-1]}

        self.driver.get(url)
        sleep(randint(100, 500)/100)
        soup = BeautifulSoup(self.driver.page_source, "lxml")

        certificates_pages_num = get_page_num(soup, 'certifdicate')
        bits_pages_num = get_page_num(soup, 'bid')
        patents_pages_num = get_page_num(soup, 'patent')
        copyrights_pages_num = get_page_num(soup, 'copyright')

        self.crawl_info(soup, result)
        self.crawl_certificates(result, certificates_pages_num, result['company_id'])
        self.crawl_bits(result, bits_pages_num, result['company_id'])
        self.crawl_patents(result, patents_pages_num, result['company_id'])
        self.crawl_copyrights(result, copyrights_pages_num, result['company_id'])
        pprint(result)
        return result

    def crawl_certificates(self, result, pages_num, company_id):
        """
        :param result: dict
        :param pages_num: int
        :param company_id: str
        """
        url_fmt = "https://www.tianyancha.com/pagination/certificate.xhtml?ps=5&pn={page}&id={c_id}"
        result['company_certificate'] = []
        for page in range(1, pages_num + 1):
            url = url_fmt.format(page=page, c_id=company_id)
            self.driver.get(url)
            sleep(randint(100, 300)/100)

            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            trs = soup.findAll('tr')
            for tr in trs[1:]:
                result['company_certificate'].append(tr.findAll('td')[1].getText())

    def crawl_bits(self, result, pages_num, company_id):
        """
        :param result: dict
        :param pages_num: int
        :param company_id: str
        """
        result['company_bits'] = []
        url_fmt = "https://www.tianyancha.com/pagination/bid.xhtml?ps=10&pn={page}&id={c_id}"
        for page in range(1, pages_num + 1):
            url = url_fmt.format(page=page, c_id=company_id)
            self.loginer.try_get(url)
            sleep(randint(100, 300)/100)

            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            trs = soup.findAll('tr')
            for tr in trs[1:]:
                try:
                    bit = {}
                    tds = tr.findAll('td')
                    bit['index'] = tds[0].getText()
                    bit['time'] = tds[1].getText()
                    bit['title'] = next(tds[2].descendants).getText()
                    bit['owner'] = next(tds[3].descendants)
                    result['company_bits'].append(bit)
                except (AttributeError, IndexError):
                    pass

    def crawl_patents(self, result, pages_num, company_id):
        """
        :param result: dict
        :param pages_num: int
        :param company_id: str
        """
        result['company_patents'] = []
        url_fmt = "https://www.tianyancha.com/pagination/patent.xhtml?ps=5&pn={page}&id={c_id}"
        for page in range(1, pages_num + 1):
            url = url_fmt.format(page=page, c_id=company_id)
            self.loginer.try_get(url)
            sleep(randint(100, 300)/100)

            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            trs = soup.findAll('tr')
            for tr in trs[1:]:
                patent = {}
                try:
                    tds = tr.findAll('td')
                    patent['index'] = tds[0].getText()
                    patent['time'] = tds[1].getText()
                    patent['patent_num'] = tds[2].getText()
                    patent['apply_number'] = tds[3].getText()
                    patent['patent_apply'] = tds[4].getText()
                    patent['patent_type'] = tds[5].getText()
                    patent['detail'] = tds[6].find('a')['href']
                    result['company_patents'].append(patent)
                except (AttributeError, TypeError):
                    pass

    def crawl_copyrights(self, result, pages_num, company_id):
        """
        :param result: dict
        :param pages_num: int
        :param company_id: str
        """
        result['company_copyrights'] = []
        url_fmt = "https://www.tianyancha.com/pagination/copyright.xhtml?ps=5&pn={page}&id={c_id}"
        for page in range(1, pages_num + 1):
            url = url_fmt.format(page=page, c_id=company_id)
            self.loginer.try_get(url)
            sleep(randint(100, 300) / 100)

            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            trs = soup.findAll('tr')
            for tr in trs[1:]:
                try:
                    cr = {}
                    tds = tr.findAll('td')
                    cr['index'] = tds[0].getText()
                    cr['time'] = tds[1].getText()
                    cr['software_name'] = tds[2].getText()
                    cr['software_simple_name'] = tds[3].getText()
                    cr['copyright_number'] = tds[4].getText()
                    cr['type_number'] = tds[5].getText()
                    cr['version_number'] = tds[6].getText()
                    result['company_copyrights'].append(cr)
                except (AttributeError, TypeError):
                    pass

    @staticmethod
    def crawl_info(soup, result):
        """
        :param soup: BeautifulSoup
        :param result: dict
        """
        result['company_name'] = soup.find('h1', class_="name").getText()

        details = soup.find('div', class_='detail').find_all('div', class_='in-block')
        try:
            result['company_phone'] = details[0].find('script').getText()
        except AttributeError:
            result['company_phone'] = '暂无消息'
        try:
            result['company_email'] = details[1].find('script').getText()
        except AttributeError:
            result['company_email'] = '暂无消息'
        try:
            result['company_website'] = details[2].find('a', class_='company-link').getText()
        except AttributeError:
            result['company_website'] = '暂无消息'
        address = details[3].find('script')
        if address:
            result['company_address'] = address.getText()
        else:
            result['company_address'] = details[3].getText().lstrip('地址：')
         try:
            result['company_summary'] = soup.find('script', id='company_base_info_detail').getText().strip()
        except AttributeError:
            result['company_sumary'] = '暂无消息'
        block_detail = soup.find('div', class_='data-content').find_all('td')

        try:
            # 注册资本
            result['company_money'] = block_detail[4].find('text', class_='tyc-num lh24').get_text().strip()
            # 注册时间
            company_time = block_detail[6].find('div', title=' ').find('text')
            result['company_time'] = company_time.get_text().strip()
            # 公司状态
            company_situation = block_detail[7].find('div', class_='num-opening')
            result['company_situation'] = company_situation.get_text().strip()
            # 公司法定代表人
            company_humancompany = soup.find('div', class_='humancompany').find('div', class_='name').find('a')
            result['company_humancompany'] = company_humancompany['title']
        except (AttributeError, TypeError, IndexError):
            pass

        try:
            detail_table2 = soup.find('table', class_='table -striped-col -border-top-none')
            details = detail_table2.find_all('td')
            result['company_register_number'] = details[1].get_text()  # 工商注册号
            result['company_organization_code'] = details[3].get_text()  # 组织机构代码
            result['company_believe_code'] = details[6].get_text()  # 统一信用代码
            result['company_type'] = details[8].get_text()  # 公司类型
            result['company_taxpayer_identification'] = details[10].get_text()  # 纳税人识别号
            result['company_industry'] = details[12].get_text()  # 行业
            result['company_deadline'] = details[14].get_text()  # 营业期限
            result['company_check_date'] = details[16].get_text()  # 核准日期
            result['company_taxpayer_aptitude'] = details[18].get_text()  # 纳税人资质
            result['company_size'] = details[20].get_text()  # 人员规模
            result['company_real_capital'] = details[22].get_text()  # 公司实缴资本
            # 注册地址
            result['company_register_address'] = details[30].get_text()
            # 经营范围
            result['company_rate'] = soup.find('span', class_='js-full-container hidden').getText()
        except (AttributeError, TypeError, IndexError):
            pass
        pprint(result)


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
