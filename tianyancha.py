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



ent_fix = [
'测绘',
#'地理'
]


class TianyanchaLogin(object):

     def __init__(self):
         try:
             self.driver = None
             dcap = dict(DesiredCapabilities.PHANTOMJS)
             dcap["phantomjs.page.settings.userAgent"] = (
                 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0 "
             )
             self.driver = webdriver.Chrome(executable_path="./chromedriver.exe", desired_capabilities=dcap)
             self.driver.implicitly_wait(10)

             self.driver.get('https://www.tianyancha.com/login')
             time.sleep(3.0)
                                                       # ('//*[@id = "web-content"]/div/div/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/input')
             element = self.driver.find_element_by_xpath('//*[@id="web-content"]/div/div/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/input')
             element.clear()
             element.send_keys(u'yorphone')
             element = self.driver.find_element_by_xpath('//*[@id="web-content"]/div/div/div/div[2]/div/div[2]/div[2]/div[2]/div[3]/input')
             element.clear()
             element.send_keys(u'yourpasswd')

             element = self.driver.find_element_by_xpath('//*[@id="web-content"]/div/div/div/div[2]/div/div[2]/div[2]/div[2]/div[5]')
             element.click()
             time.sleep(10.0)
         except Exception:
             print(traceback.format_exc())
             print('异常退出')
             if self.driver:
                 self.driver.close()



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

        self.driver.implicitly_wait(10)

        self.mongo_env = os.environ.get('MONGO_ENV')
        if self.mongo_env:
            self.client = pymongo.MongoClient(host="mongodb://127.0.0.1", port=27017)
        else:
            self.client = pymongo.MongoClient()
        self.db = self.client['db_tyc']

    def run(self):
        for i, ent in enumerate(ent_fix):
            time.sleep(3.0)
            try:
                # 搜索公司
                data = {'key': ent}
                comp_link = u'https://www.tianyancha.com/search?' + urlencode(data)
                self.driver.get(comp_link)
                time.sleep(3)

                # 访问公司详细信息的网址
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                divs = soup.find_all('div', class_='search-result-single')
                for div in divs:
                    #print(div)
                    a = div.find('a')
                    href = a['href']
                    print(href)
                    comp_link = href
                    self.driver.get(comp_link)
                    time.sleep(2.0)

                # 从页面提取结构化信息

                    result = self.parse_page(self.driver)
                    result['url'] = href
                    pprint(result)

                # 插入到mongodb数据的集合中
                self.db['db_tyc_collection_result'].insert(result)
                time.sleep(3.0)
            except Exception:
                print(traceback.format_exc())
                continue
        if self.driver:
            time.sleep(15.0)
            self.driver.close()

    def singlepage(self):
        f = open("links0000.txt")
        for line in f:
            _link = line.strip()
            print(_link)

       # loginer = TianyanchaLogin()
       # self.driver = loginer.driver

        #self.driver.implicitly_wait(5)
        #_link = 'https://www.tianyancha.com/company/3844284'
        #_link = 'https://www.tianyancha.com/company/824093561'


            self.driver.get(_link)
        #time.sleep(2.0)
            result = {}
            result['url'] = _link
            result = self.parse_page(self.driver ,_link)
       # 插入到mongodb数据的集合中

            pprint(result)
            self.db['db_tyc_collection_result'].insert(result)
            time.sleep(3.0)



    def prase_bit_page(self, driver, num, id):
        indexes =num
        company_bits = {}
        index = 0
        for i in range(1, indexes):
            bit_url = 'https://www.tianyancha.com/pagination/bid.xhtml?ps=10&pn='+ str(i) +'&id='+ str(id)
           #&id=3844284'
            try:
                self.driver.get(bit_url)
            except selenium.common.exceptions:
                loginer = TianyanchaLogin()
                self.driver = loginer.driver
                self.driver.get(bit_url)
                continue
            except:
                continue

            bit_soup = BeautifulSoup(driver.page_source, 'lxml', from_encoding='utf-8')
            bits = bit_soup.find_all('td')
       # print(bits)

            for j in range(0, len(bits), 4):
                try:
            # company_bits[num]
                    num = 'index' + str(index)
                    company_bits[num] = {}
                    company_bits[num]['index'] = bits[j].get_text()
                    company_bits[num]['time'] = bits[j + 1].get_text()
                    company_bits[num]['title'] = bits[j + 2].get_text()
                    company_bits[num]['onwer'] = bits[j + 3].get_text()
                    index = index + 1
                except:
                    continue
           # time.sleep(5)
       # print(company_bits)
        #driver.close()
        return company_bits


   # 软件专利 https://www.tianyancha.com/pagination/patent.xhtml?ps=5&pn=61&id=3844284
    def patent_page(self, driver, num, id):
        #loginer = TianyanchaLogin()
        #self.driver = loginer.driver
        indexes = num
        company_patents = {}
        index = 0
       # id = 3844284
        for i in range(1,int(indexes)):
            patent_url = 'https://www.tianyancha.com/pagination/patent.xhtml?ps=5&pn=' + str(i) + '&id=' + str(id)
       # patent_url = 'https://www.tianyancha.com/pagination/patent.xhtml?ps=5&pn=1&id=3844284'
            try:
                self.driver.get(patent_url)
            except selenium.common.exceptions:
                loginer = TianyanchaLogin()
                self.driver = loginer.driver
                self.driver.get(patent_url)
                continue
            except:
                continue
           # self.driver.get(patent_url)
            patent_soup = BeautifulSoup(driver.page_source, 'lxml', from_encoding='utf-8')
            patents = patent_soup.find_all('td')

            #print(len(patents))

            for j in range(0,len(patents),7):
                try:
                    num = 'index' + str(index)
                    company_patents[num] = {}
            #print(patents[i+4])
                    company_patents[num]['index'] = patents[j].get_text()
                    company_patents[num]['time'] = patents[j + 1].get_text()
                    company_patents[num]['patent_name'] = patents[j + 2].get_text()
                    company_patents[num]['apply_number'] = patents[j + 3].get_text()
                    company_patents[num]['patent_apply'] = patents[j + 4].get_text()
                    company_patents[num]['patent_type'] = patents[j + 5].get_text()
                    company_patents[num]['detail'] = patents[j + 6].find('a')['href']
                    index = index + 1
                except:
                    continue
            #time.sleep(5)
        #driver.close()
        return company_patents

# 软件著作权 https://www.tianyancha.com/pagination/copyright.xhtml?ps=5&pn=1&id=3844284
    def copyright_page(self, driver, num, id):
       # loginer = TianyanchaLogin()
        #self.driver = loginer.driver
        #copyright_utl = 'https://www.tianyancha.com/pagination/copyright.xhtml?ps=5&pn=1&id=3844284'
        indexes = num
        company_copyright = {}
        index = 0
        loginer = TianyanchaLogin()
        self.driver = loginer.driver
        for i in range(1, int(indexes)):
            copyright_url = 'https://www.tianyancha.com/pagination/copyright.xhtml?ps=5&pn=' + str(i) + '&id=' + str(id)
            #self.driver.get( copyright_utl)
            try:
                self.driver.get(copyright_url)
            except selenium.common.exceptions:
                loginer = TianyanchaLogin()
                self.driver = loginer.driver
                self.driver.get(copyright_url)
                continue
            except:
                continue
            copyright_soup = BeautifulSoup(driver.page_source, 'lxml', from_encoding='utf-8')
            copyrights = copyright_soup.find_all('td')

            for j in range(0, len(copyrights), 8):
                try:
                    num = 'index' + str(index)
                    company_copyright[num] = {}
            # print(patents[i+4])
                    company_copyright[num]['index'] = copyrights[j].get_text()
                    company_copyright[num]['time'] = copyrights[j + 1].get_text()
                    company_copyright[num]['software_name'] = copyrights[j + 2].get_text()
                    company_copyright[num]['software_simple_name'] = copyrights[j + 3].get_text()
                    company_copyright[num]['copyright_number'] = copyrights[j + 4].get_text()
                    company_copyright[num]['type_number'] = copyrights[j + 5].get_text()
                    company_copyright[num]['version_number'] = copyrights[j + 6].get_text()
                    company_copyright[num]['detail'] = copyrights[j + 7].get_text().strip()
                    index = index + 1
                except:
                    continue
                #time.sleep(5)
        driver.close()
        return company_copyright

    def parse_page(self, driver, _link):

        # 划动到最底边，让浏览器加载js脚本并执行
       # self.driver.execute_script(
            #"window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        time.sleep(2)
        result = {}
        result['url'] = _link
        try:
            soup = BeautifulSoup(driver.page_source, 'lxml',from_encoding='utf-8')
           # print(soup)


            #basic_info
            temp_string = soup.find('div', class_='content')
            company_name = temp_string.find_all('h1')
            #company_name = company_name.find('h1').get_text()
            #print(company_name)


            for name in company_name:
                result['company_name'] = name.get_text()
            infos= temp_string.find('div',class_='detail' ).find_all('div', class_="in-block")

            result['company_phone'] = infos[0].get_text() #联系电话
            result['company_email'] = infos[1].get_text().split('查看更多')[0] #联系邮箱
            result['company_wesite'] = infos[2].get_text() #网址
            result['company_address'] = infos[3].get_text() #地址

            summary = temp_string.find('div', class_='detail').find('div', class_="summary") #简介
            result['company_summary'] = summary.get_text()
            
            block_detail = soup.find('div', class_='data-content').find_all('td')
            #for dt in block_detail:
             #   print(dt)
            #print(block_detail)
            #注册资本
            #result['company_money'] =  block_detail[4].find_all('div', title='-')[0].get_text()
            #注册时间
            try:
                company_time = block_detail[6].find('div', title=' ').find('text')
                result['company_time'] = company_time.get_text()
                company_situation = block_detail[7].find('div', title='存续')
                result['company_situation'] = company_situation.get_text()
                company_humancompany = soup.find('div', class_='humancompany').find('div', class_='name').find('a')
                result['company_humancompany'] = company_humancompany['title']
            except:
                pass
            #result['company_time'] = company_time.get_text()
            #公司状态
            #company_situation = block_detail[7].find('div', title='存续')
            #result['company_situation'] = company_situation.get_text()
            #法定代表人
            # company_humancompany = soup.find('div', class_='humancompany').find('div', class_='name').find('a')
            # result['company_humancompany'] = company_humancompany['title']

                #print(details)
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

            ###资质证书
            company_certificate ={}
            try:
                js1 = "goToPage('nav-main-manageStatus')"
                driver.execute_script(js1)
                driver.find_element_by_id('nav-main-certificateCount')
                zizhi_soup = BeautifulSoup(driver.page_source, 'lxml', from_encoding='utf-8')
                zizhi = zizhi_soup.select('#nav-main-certificateCount')[0]
                #资质证书
                zizhi = zizhi.find_all('div', class_='item')
                index  = 0
                for i in zizhi:
                    num = 'index' + str(index)
                    company_certificate[num] = i.get_text()
                    index = index+1
                    #print(company_certificate)
            except:
                pass

            result['company_certificate'] = company_certificate

            js1 = "goToPage('nav-main-manageStatus')"
            driver.execute_script(js1)
            bit_soup = BeautifulSoup(driver.page_source, 'lxml', from_encoding='utf-8')

            ###中标
            id = result['url']
            id = int(id.split('/')[-1])

           # bits = bit_soup.select('#_container_bid')[0]
            try:
                bits_soup = bit_soup.select('#_container_bid')[0]
                total_nums = bits_soup.find('a', class_='num -end').get_text()[3:]
            except:
                total_nums = 10
            total_nums=(int(total_nums)-1)
            #print(bit_url_id)
            company_bits = clawer.prase_bit_page(self.driver, total_nums,id)


            ###专利信息
            id = result['url']
            id = int(id.split('/')[-1])
           # patents_soup = bit_soup.select('#_container_patent')[0]
            try:
                patents_soup = bit_soup.select('#_container_patent')[0]
                total_patents_nums = patents_soup.find('a', class_='num -end').get_text()[3:]
            except:
                total_patents_nums = 10
            total_patents_nums = (int(total_patents_nums) - 1)
            #print(total_patents_nums)

            company_patents = clawer.patent_page(self.driver, total_patents_nums, id)
            # print(company_patents)


            ### 软件著作权
            #copyright_soup = bit_soup.select('#_container_copyright')[0]
            try:
                copyright_soup = bit_soup.select('#_container_copyright')[0]
                total_copyright_nums =  copyright_soup.find('a', class_='num -end').get_text()[3:]
            except:
                total_copyright_nums = 10
            total_copyright_nums = (int( total_copyright_nums) - 1)
            #print(total_copyright_nums)
            company_copyright = clawer.copyright_page(self.driver, total_copyright_nums, id)
           # print(company_copyright)


            result['company_copyright'] = company_copyright
            result['company_patents'] = company_patents
            result['company_bits'] = company_bits

            #翻页
            # num = 0
            # for j in range(3):
            #     bits = bit_soup.select('#_container_bid')[0].find_all('td')
                # 中标公告
                #num = 0
                #for i in range(0,len(bits), 4):
                 #   #company_bits[num]
                  #  company_bits[num] = {}
                 # company_bits[num]['index'] = bits[i].get_text()
                 #    company_bits[num]['time'] = bits[i+1].get_text()
                 #    company_bits[num]['title'] = bits[i+2].get_text()
                 #    company_bits[num]['onwer'] = bits[i+3].get_text()
                 #    num = num+1
                # time.sleep(3)
                #element_bit = self.driver.find_element_by_xpath('//*[@id="_container_bid"]/div/ul/li[12]/a')
                #driver.execute_script('companyPageChange(2,this)')
                #element = self.driver.find_element_by_xpath(
                  #  '//*[@id="web-content"]/div/div/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/input')

                # element_bit.click()
                # time.sleep(3)



        #driver.close()

        except Exception:
            print(traceback.format_exc())
        return result


if __name__ == "__main__":
# TianyanchaLogin()
    clawer = TianyanchaClawer()
    #clawer.run()
    clawer.singlepage()
