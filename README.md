# Project-02 TianyanSpider

use the selenium and Chrome tools implements crawl tianyan companie's data and store it into mongodb.																		

### Project Description

通过给定的关键字爬取相关公司信息，本项目针对关键字 ‘测绘’、‘地理信息’等进行数据爬取，然后将数据存进 MongoDB。


### Environment
	
+ Python3.6.3
+ Selenium 3.8.0
+ Chromedriver V2.41
+ Chrome 版本 67.0.3396.99

chromedriver 镜像地址可查看 [npm.taobao.org](http://npm.taobao.org/mirrors/chromedriver/)
    
### Importance

由于项目采用 selenium、Chrome，请注意 Chrome 与 Chromedriver 的问题。并把 Chromedriver 加入 PATH。版本匹配问天眼搜索查询普通用户仅支持 100 家，VIP用户支持 5000 家。详情页大部分信息则不受 VIP限制。

### Usage

test.py:

```Python
#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-

"""
导入三个包：
tyc_login：登录模块；
tyc_urls_crawler：链接爬取模块；
tyc_singlepage_crawler：详细页爬取模块。
"""

from tyc_spider import tyc_login
from tyc_spider import tyc_urls_crawler
from tyc_spider import tyc_singlepage_crawler


# 登录爬虫两个参数，电话号码跟密码
PHONE = 'phone'
PASSWORD = 'password'

# 关键词列表
KEYWORDS = ['航空仿真摄影']

# 登录
login_driver = tyc_login.TianyanchaLogin(PHONE, PASSWORD)

# 初始化 URL 爬虫
url_crawler = tyc_urls_crawler.TianyanchaUrlsCrawler(login_driver.driver, KEYWORDS)

# 爬取返回 URL 列表
urls = url.crawl_urls()

# 初始化详细页爬虫
single_page_crawl = tyc_singlepage_crawler.TianyanchaSinglePageClawer(login_driver)

# 爬取信息，返回字典 result，自行对其处理
for link in urls:
    result = single_page_crawl.crawl_single_page(link)
```

### Data model


爬取数据示例：

```
{'company_address': '地址：',
 'company_believe_code': '91510700205418339Y',
 'company_check_date': '1594-56-17',
 'company_deadline': '1994-12-26至无固定期限',
 'company_email': '["jinggb@jezetek.cc"]',
 'company_humancompany': '杜力平',
 'company_id': '163142626',
 'company_industry': '计算机、通信和其他电子设备制造业',
 'company_money': '155555万人民币',
 'company_name': '四川九洲电器集团有限责任公司',
 'company_organization_code': '205418339',
 'company_phone': '["0816-2468306"]',
 'company_rate': '雷达及配套设备、通信设备、物联网设备、广播电视设备、电线、电缆、光缆、电工器材、光电子器件及半导体照明软硬件制造和销售，智能建筑系统、安全防范系统、消防系统、城市照明系统、计算机信息系统集成服务及相关设备器材的设计、制造、安装、销售，软件开发，智慧城市的规划、设计、咨询以及相关智能系统工程的施工、运营、维护，新材料的技术研究和技术服务，普通机械及零部件加工，房地产开发、经营（取得资质证后方可经营），物业管理，出口自产机电产品，进口批准的所需原辅材料、设备、仪器及零配件，承包境外电子行业工程及境内国际招标工程，汽车维修。（依法须经批准的项目，经相关部门批准后方可开展经营活动）雷达及配套设备、通信设备、物联网设备、广播电视设备、电线、电缆、光缆、电工器材、光电子器件及半导体照明软硬件制造和销售，智能建筑系统、安全防范系统、消防系统、城市照明系统、计算机信息系统集成服务及相关设备器材的设计、制造、安装、销售，软件开发，智慧城市的规划、设计、咨询以及相关智能系统工程的施工、运营、维护，新材料的技术研究和技术服务，普...详情',
 'company_real_capital': '150000万人民币',
 'company_register_address': '四川省绵阳市九华路6号附近公司',
 'company_register_number': '510700000059847',
 'company_situation': '存续',
 'company_size': '1000-4999人',
 'company_summary': '四川九洲电器集团有限责任公司，于1958年在绵阳成立，是国家“一五”期间156项重点工程之一，是国家唯一保留核心科研生产能力的地方军工骨干企业。成立至今，九洲由单一军工厂发展为以军事电子、智慧城市为核心业务高科技企业集团。公司现已形成了基础产业、目标产业、机会产业、综合产业等四大类产业，为国家二次雷达系统产品的科研生产基地，空管系统及设备科研生产基地，数字电视设备和有线电视网络设备的研发、制造基地，西部最大的LED产业基地。',
 'company_taxpayer_aptitude': '-',
 'company_taxpayer_identification': '91510700205418339Y',
 'company_time': '9660-91-13',
 'company_type': '有限责任公司(国有独资)',
 'company_website': 'http://www.jezetek.cc',
 'url': 'https://www.tianyancha.com/company/163142626'}
```

### Hisory Version

+ 2018-08-21
    1. 解耦爬虫为三个模块（登录、公司链接爬取、公司详细页爬取）
    2. 代码格式优化、删除不需要的代码
    3. 调整爬取速度，添加随机
    4. 添加使用说明

+ 2018-08-13

	1. 修改数据结构存储格式
	2. 完善链接列表的获取
	3. 将数据进行了轻微的清理
	4. 调整爬取速度

+ 2018-08-07
  
  实现：公司基本信息包括，网址、注册时间、注册地点、法定代表人、经营范围、公司规模、公司专利、软件著作权、招标等信息
  
  缺点：爬虫速度过快、爬取数据量过大易引起天眼查的反爬策略，常见的为验证码问题以及账号登入问题。由于请求的数据多达2万条，总体爬虫效率较低，爬虫速度待改进。
 
  
