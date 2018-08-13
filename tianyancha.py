import os
import time
import pymongo
import traceback
from pprint import pprint
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import selenium.common
import string
try:
    from urllib import urlencode
except:
    from urllib.parse import urlencode

# 请把关键字放这
keywords = [
    '测绘',
    # '地理'
]

# 天眼自动登入
class TianyanchaLogin(object):

    def __init__(self):
        try:
            self.driver = None
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.userAgent"] = (
                 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0 "
             )
            self.driver = webdriver.Chrome(executable_path="./chromedriver.exe", desired_capabilities=dcap)
            self.driver.implicitly_wait(5)

            self.driver.get('https://www.tianyancha.com/login')
            time.sleep(2.0)

            element = self.driver.find_element_by_xpath('//*[@id="web-content"]/div/div/div/div[2]/div/div[2]'
                                                        '/div[2]/div[2]/div[2]/input')
            element.clear()
            element.send_keys(u'yourphone')
            element = self.driver.find_element_by_xpath('//*[@id="web-content"]/div/div/div/div[2]/div/div[2]'
                                                        '/div[2]/div[2]/div[3]/input')
            element.clear()
            element.send_keys(u'yourpasswd')

            element = self.driver.find_element_by_xpath('//*[@id="web-content"]/div/div/div/div[2]/div/div[2]'
                                                        '/div[2]/div[2]/div[5]')
            element.click()
            time.sleep(5.0)
        except Exception:
            print(traceback.format_exc())
            print('异常退出')
            if self.driver:
                self.driver.close()



# 天眼数据爬取
class TianyanchaClawer(object):

    def __init__(self):

        self.driver = None
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0 "
        )
        self.env = os.environ.get('CHROME_DRIVER_ENV')
        if self.env:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-setuid-sandbox")
            self.driver = webdriver.Chrome(chrome_options=chrome_options)
        else:
            self.driver = webdriver.Chrome(desired_capabilities=dcap)

        loginer = TianyanchaLogin()
        self.driver = loginer.driver

        self.driver.implicitly_wait(3)

        self.mongo_env = os.environ.get('MONGO_ENV')
        if self.mongo_env:
            self.client = pymongo.MongoClient(host="mongodb://127.0.0.1", port=27017)
        else:
            self.client = pymongo.MongoClient()
        self.db = self.client['db_tyc_data']

    def run(self):
        for i, keyword in enumerate(keywords):
            # time.sleep(3.0)
            try:
                # 按关键字搜索公司
                data = {'key': keyword}
                # 构造请求链接
                comp_link = u'https://www.tianyancha.com/search?' + urlencode(data)
                self.driver.get(comp_link)
                time.sleep(1)

                # 访问公司详细信息的网址
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                # 获取页数
                pages_num = soup.find('a', class_='num -end').get_text()[3: ]
                print(pages_num)
                # 用于测试时可以另 pages_num = 2,便于程序调试

                urls_lists = self.save_links_list(pages_num, data)

                print(urls_lists)
                # 重新构造爬取链接
                for url in urls_lists:
                    # comp_link = href
                    #self.driver.get(url)
                    # 从页面提取结构化信息
                    self.singlepage(url)
                    time.sleep(1.0)
                # 跑完关闭
                self.driver.close()
            except Exception:
                print(traceback.format_exc())
                continue
        if self.driver:
            time.sleep(8.0)
            self.driver.close()

    # 返回所有链接列表
    def save_links_list(self, pages_num, data):
        lists = []
        # 重新构造爬取链接
        for num in range(1, pages_num):
            # 链接列表
            lists_link = u'https://www.tianyancha.com/search/p' + str(num) + '?' + urlencode(data)
            self.driver.get(lists_link)
            time.sleep(1)
            # 访问公司详细信息的网址
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            divs = soup.find_all('div', class_='search-result-single')
            for div in divs:
                # print(div)
                a = div.find('a')
                href = a['href']
                #print(href)
                # 加入列表
                lists.append(href)
        return lists

    # 单页详情页调度
    #  driver, _link
    def singlepage(self,  _link):
        # 如果链接已保存在相应文件，可以去掉该注释
        #f = open("new_links0000.txt")#new_links0000.txt
        #for line in f:
           # _link = line.strip()
            #print(_link)
        #time.sleep(2.0)
           # _link = 'https://www.tianyancha.com/company/3844284'

            self.driver.get(_link)
            result = {}
            result['url'] = _link
            result = self.parse_page(self.driver, _link)
            # 插入到mongodb数据的集合中
            pprint(result)
            self.db['db_tyc_collection_data'].insert(result)
            time.sleep(2.0)

    #中标
    def prase_bit_page(self, driver, num, id):
        company_bits = []
        for i in range(1, num):
            bit_url = 'https://www.tianyancha.com/pagination/bid.xhtml?ps=10&pn='+ str(i) +'&id='+ str(id)
           #&id=3844284'
            try:
                self.driver.get(bit_url)
            except selenium.common.exceptions:
                loginer = TianyanchaLogin()
                self.driver = loginer.driver
                self.driver.get(bit_url)
                pass
            except:
                pass

            bit_soup = BeautifulSoup(driver.page_source, 'lxml', from_encoding='utf-8')
            bits = bit_soup.find_all('td')
            for j in range(0, len(bits), 4):
                try:
                    bit = {}
                    bit['index'] = bits[j].get_text()
                    bit['time'] = bits[j + 1].get_text()
                    bit['title'] = bits[j + 2].get_text()
                    bit['onwer'] = bits[j + 3].get_text()
                    company_bits['company_bits'].append(bit)
                except:
                   pass
        time.sleep(2)
        # print(company_bits)
        return company_bits


   # 软件专利 https://www.tianyancha.com/pagination/patent.xhtml?ps=5&pn=61&id=3844284
    def patent_page(self, driver, num, id):
        company_patents = []
       # id = 3844284
        for i in range(1,int(num)):
            patent_url = 'https://www.tianyancha.com/pagination/patent.xhtml?ps=5&pn=' + str(i) + '&id=' + str(id)
       # patent_url = 'https://www.tianyancha.com/pagination/patent.xhtml?ps=5&pn=1&id=3844284'
            try:
                self.driver.get(patent_url)
            except selenium.common.exceptions:
                loginer = TianyanchaLogin()
                self.driver = loginer.driver
                self.driver.get(patent_url)
                pass
            except:
                pass
            patent_soup = BeautifulSoup(driver.page_source, 'lxml', from_encoding='utf-8')
            patents = patent_soup.find_all('td')
            for j in range(0, len(patents), 7):
                try:
                    patent = {}
                    patent['index'] = patents[j].get_text()
                    patent['time'] = patents[j + 1].get_text()
                    patent['patent_name'] = patents[j + 2].get_text()
                    patent['apply_number'] = patents[j + 3].get_text()
                    patent['patent_apply'] = patents[j + 4].get_text()
                    patent['patent_type'] = patents[j + 5].get_text()
                    patent['detail'] = patents[j + 6].find('a')['href']
                    company_patents.append(patent)
                except:
                    pass
        time.sleep(2)
        # print(company_patents)
        return company_patents

# 软件著作权 https://www.tianyancha.com/pagination/copyright.xhtml?ps=5&pn=1&id=3844284
    def copyright_page(self, driver, num, id):
        company_copyright = []
        for i in range(1, int(num)):
            copyright_url = 'https://www.tianyancha.com/pagination/copyright.xhtml?ps=5&pn=' + str(i) + '&id=' + str(id)
            try:
                self.driver.get(copyright_url)
            except selenium.common.exceptions:
                loginer = TianyanchaLogin()
                self.driver = loginer.driver
                self.driver.get(copyright_url)
                pass
            except:
                pass
            copyright_soup = BeautifulSoup(driver.page_source, 'lxml', from_encoding='utf-8')
            copyrights = copyright_soup.find_all('td')

            for j in range(0, len(copyrights), 8):
                try:
                    copyright = {}
                    copyright['index'] = copyrights[j].get_text()
                    copyright['time'] = copyrights[j + 1].get_text()
                    copyright['software_name'] = copyrights[j + 2].get_text()
                    copyright['software_simple_name'] = copyrights[j + 3].get_text()
                    copyright['copyright_number'] = copyrights[j + 4].get_text()
                    copyright['type_number'] = copyrights[j + 5].get_text()
                    copyright['version_number'] = copyrights[j + 6].get_text()
                    copyright['detail'] = copyrights[j + 7].get_text().strip()
                    company_copyright.append(copyright)
                except:
                    pass

        time.sleep(2)
        # print(company_copyright)
        return company_copyright

    def parse_page(self, driver, _link):

        result = {}
        result['url'] = _link
        try:
            soup = BeautifulSoup(driver.page_source, 'lxml',from_encoding='utf-8')
            #basic_info
            temp_string = soup.find('div', class_='content')
            company_name = temp_string.find_all('h1')
            #company_name = company_name.find('h1').get_text()
            #print(company_name)


            for name in company_name:
                result['company_name'] = name.get_text().strip()
            infos = temp_string.find('div', class_='detail').find_all('div', class_="in-block")

            result['company_phone'] = infos[0].get_text().split('查看更多') #联系电话
            result['company_email'] = infos[1].get_text().split('查看更多')[0] #联系邮箱
            result['company_wesite'] = infos[2].get_text().strip() #网址
            result['company_address'] = infos[3].get_text().strip() #地址

            summary = temp_string.find('div', class_='detail').find('div', class_="summary") #简介
            result['company_summary'] = summary.get_text().strip()
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
            except:
                pass

            try:
                detail_table2 = soup.find('table' , class_='table -striped-col -border-top-none')
                details = detail_table2.find_all('td')
                result['company_register_number'] = details[1].get_text() #工商注册号
                result['company_organization_code'] = details[3].get_text() #组织机构代码
                result['company_believe_code'] = details[6].get_text() #统一信用代码
                result['company_type'] = details[8].get_text() # 公司类型
                result['company_taxpayer_identification'] = details[10].get_text()#纳税人识别号
                result['company_industry'] = details[12].get_text()#行业
                result['company_deadline'] = details[14].get_text()#营业期限
                result['company_check_date'] =  details[16].get_text()#核准日期
                result['company_taxpayer_aptitude'] = details[18].get_text() #纳税人资质
                result['company_size'] = details[20].get_text()#人员规模
                result['company_real_capital'] =details[22].get_text() #公司实缴资本
                 #注册地址
                result['company_register_address'] = details[30].get_text()
                 #经营范围
                result['company_rate'] = details[32].get_text()
            except:
                pass

            # 资质证书
            company_certificate = []
            try:
                js1 = "goToPage('nav-main-manageStatus')"
                driver.execute_script(js1)
                driver.find_element_by_id('nav-main-certificateCount')
                zizhi_soup = BeautifulSoup(driver.page_source, 'lxml', from_encoding='utf-8')
                zizhi = zizhi_soup.select('#nav-main-certificateCount')[0]
                #资质证书
                zizhi = zizhi.find_all('div', class_='item')
                for i in zizhi:
                    certificate = i.get_text()
                    print(certificate)
                    company_certificate.append(certificate)
            except:
                pass

            result['company_certificate'] = company_certificate

            js1 = "goToPage('nav-main-manageStatus')"
            #driver.execute_script(js1)
            bit_soup = BeautifulSoup(driver.page_source, 'lxml', from_encoding='utf-8')

            # 中标投标信息
            id = result['url']
            id = int(id.split('/')[-1])

           # bits = bit_soup.select('#_container_bid')[0]
            try:
                bits_soup = bit_soup.select('#_container_bid')[0]
                total_nums = bits_soup.find('a', class_='num -end').get_text()[3:]
            except:
                #total_nums = 2
                pass
            try:
                total_nums = (int(total_nums)-1)
                company_bits = clawer.prase_bit_page(self.driver, total_nums, id)
                result['company_bits'] = company_bits
            except:
                pass


            # 专利信息
            id = result['url']
            id = int(id.split('/')[-1])
           # patents_soup = bit_soup.select('#_container_patent')[0]
            try:
                patents_soup = bit_soup.select('#_container_patent')[0]
                total_patents_nums = patents_soup.find('a', class_='num -end').get_text()[3:]
                if total_patents_nums> 30:
                    total_patents_nums = 30
            except:
                #total_patents_nums = 10
                pass
            try:
                total_patents_nums = (int(total_patents_nums) - 1)
                company_patents = clawer.patent_page(self.driver, total_patents_nums, id)
                result['company_patents'] = company_patents
            except:
                pass

            # 软件著作权
            try:
                copyright_soup = bit_soup.select('#_container_copyright')[0]
                total_copyright_nums =  copyright_soup.find('a', class_='num -end').get_text()[3:]
                if total_copyright_nums > 30:
                    total_copyright_nums = 30
            except:
                pass
            try:
                total_copyright_nums = (int(total_copyright_nums) - 1)
                company_copyright = clawer.copyright_page(self.driver, total_copyright_nums, id)
                result['company_copyright'] = company_copyright
            except:
                pass






        except Exception:
            print(traceback.format_exc())
        return result


if __name__ == "__main__":
# TianyanchaLogin()
    clawer = TianyanchaClawer()
    clawer.run()
    #clawer.singlepage()
