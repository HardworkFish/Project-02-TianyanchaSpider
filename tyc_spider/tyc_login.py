#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-


from time import sleep

from selenium import webdriver


# Login
class TianyanchaLogin:
    """
    登录入口，返回 driver
    """
    def __init__(self, phone, password):
        """
        :param phone: str
        :param password: str
        """
        self.phone = phone
        self.password = password
        self.driver = None
        self.login()

    def login(self):
        try:
            self.driver = webdriver.Chrome()
            self.driver.get('https://www.tianyancha.com/login')

            phone_input = self.driver.find_element_by_xpath('''//input[@onfocus="clearMsg('phone')"]''')
            phone_input.send_keys(self.phone)
            password_input = self.driver.find_element_by_xpath('''//input[@onkeyup="loginByPhone(event,'keydown')"]''')
            password_input.send_keys(self.password)
            login_button = self.driver.find_element_by_xpath('//div[@tyc-event-ch="Login.Login"]')
            login_button.click()

            sleep(3)
        except (AttributeError, TypeError):
            if self.driver:
                self.driver.close()
            raise

    def try_get(self, url):
        """
        :param url: str
        """
        self.driver.get(url)
        print(self.driver.page_source.find('Unauthorized'))
        if self.driver.page_source.find('Unauthorized') != -1:
            self.driver.close()
            self.login()
            self.driver.get(url)
