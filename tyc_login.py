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
        try:
            self.driver = webdriver.Chrome()
            self.driver.get('https://www.tianyancha.com/login')

            phone_input = self.driver.find_element_by_xpath('''//input[@onfocus="clearMsg('phone')"]''')
            phone_input.send_keys(phone)
            password_input = self.driver.find_element_by_xpath('''//input[@onkeyup="loginByPhone(event,'keydown')"]''')
            password_input.send_keys(password)
            login_button = self.driver.find_element_by_xpath('//div[@tyc-event-ch="Login.Login"]')
            login_button.click()

            sleep(3)
        except:
            if self.driver:
                self.driver.close()
            raise
