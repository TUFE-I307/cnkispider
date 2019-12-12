# -*- coding:utf-8 -*-
# Author: Qin
# @Time : 2019/10/15 14:43
# @IDE  : PyCharm
from selenium import webdriver
import re
import time
import numpy as np
import csv

def is_Chinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def keyword_path(n=2):
    return '//html/body[@class="rootw"]/div[@id="mainArea"]/div[@class="wxmain"]/div[@class="wxInfo"]/div[@class="wxBaseinfo"]/p[%d]' % n

def get_abstract(driver, abs_path):
    more_path = '//div[@id="mainArea"]/div[@class="wxmain"]/div[@class="wxInfo"]/div[@class="wxBaseinfo"]/p[1]/span[2]'
    try:
        driver.find_element_by_xpath(more_path).click()
        time.sleep(0.5)
    except:
        pass
    return driver.find_element_by_xpath(abs_path).text

def process_verification(driver):
    veri_path = '//html/body/p[1]/input[@id="CheckCode"]'
    veri_btn_path = '//html/body/p[1]/input[@type="button"]'
    try:
        driver.find_element_by_xpath(veri_path).click()
        need_veri = True
        while need_veri:
            need_veri = input_verification(driver, veri_path, veri_btn_path)
    except:
        pass

def input_verification(driver, veri_path, veri_btn_path):
    input_veri = input('输入验证码 :')
    if input_veri:
        print(input_veri)
        driver.find_element_by_xpath(veri_path).send_keys(input_veri)
        driver.find_element_by_xpath(veri_btn_path).click()
        return True
    else:
        return False

def get_topic_abstracts(topic, page_nums=10, filepath='./'):
    abstract_path = '//div[@id="mainArea"]/div[@class="wxmain"]/div[@class="wxInfo"]/div[@class="wxBaseinfo"]/p[1]/span[@id="ChDivSummary"]'
    input_path = '//div[@class="searchmain"]/div[@class="search-form"]/div[@class="input-box"]/input[@class="search-input"]'
    search_button_path = '//div[@class="searchmain"]/div[@class="search-form"]/div[@class="input-box"]/input[@class="search-btn"]'
    page_path = '/html/body/form/table/tbody/tr[3]/td/table/tbody/tr/td/div/a[last()]'
    url = 'https://www.cnki.net/'

    driver = webdriver.Firefox(executable_path='geckodriver')

    driver.get(url)
    driver.find_element_by_xpath(input_path).clear()
    driver.find_element_by_xpath(input_path).send_keys(topic)
    driver.find_element_by_xpath(search_button_path).click()
    time.sleep(7)
    driver.switch_to.frame('iframeResult')
    try:
        res = []
        count = 0
        while page_nums > 0:
            for i in range(1, 21):
                button_path = '/html/body[@class="rootw"]/form[1]/table/tbody/tr[2]/td[1]/table[@class="GridTableContent"]/tbody/tr[%d]/td[2]/a[@class="fz14"]' % (i + 1)
                author_path = '/html/body[@class="rootw"]/form[1]/table/tbody/tr[2]/td[1]/table[@class="GridTableContent"]/tbody/tr[%d]/td[@class="author_flag"]' % (i + 1)
                source_path = '/html/body[@class="rootw"]/form[1]/table/tbody/tr[2]/td[1]/table[@class="GridTableContent"]/tbody/tr[%d]/td[4]' % (i + 1)
                pubtime_path = '/html/body[@class="rootw"]/form[1]/table/tbody/tr[2]/td[1]/table[@class="GridTableContent"]/tbody/tr[%d]/td[5]' % (i + 1)
                papertype_path = '/html/body[@class="rootw"]/form[1]/table/tbody/tr[2]/td[1]/table[@class="GridTableContent"]/tbody/tr[%d]/td[6]' % (i + 1)
                process_verification(driver)
                tmp_author = driver.find_element_by_xpath(author_path).text
                tmp_source = driver.find_element_by_xpath(source_path).text
                tmp_pubtime = driver.find_element_by_xpath(pubtime_path).text
                tmp_papertype = driver.find_element_by_xpath(papertype_path).text
                button = driver.find_element_by_xpath(button_path)
                target = driver.find_element_by_xpath(button_path)
                driver.execute_script("arguments[0].scrollIntoView();", target)
                tmp_title = button.text
                button.click()
                time.sleep(1)
                driver.switch_to.window(driver.window_handles[1])
                if is_Chinese(tmp_title):# and tmp_papertype not in ['硕士', '博士']:
                    time.sleep(1)
                    try:
                        tmp_abstract = get_abstract(driver, abstract_path)
                        tmp_keywords_num = 2
                        tmp_keywords = driver.find_element_by_xpath(keyword_path(tmp_keywords_num)).text
                        while not re.match('^关键词(,*?)', tmp_keywords):
                            tmp_keywords_num += 1
                            tmp_keywords = driver.find_element_by_xpath(keyword_path(tmp_keywords_num)).text
                    except:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        time.sleep(1)
                        continue
                    res.append([tmp_title, tmp_author, tmp_source, tmp_pubtime, tmp_papertype, tmp_abstract, tmp_keywords])
                    count += 1
                    print('%s-%d %s[%s] %s'%(topic, count, tmp_title, tmp_papertype, tmp_author))
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(2)
            driver.find_element_by_xpath(page_path).click()
            page_nums -= 1
            time.sleep(2)
        driver.quit()
    except:
        driver.quit()
    res = np.array(res)
    with open(filepath + '%s.csv' % topic, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(res)
        f.close()

if __name__ == '__main__':
    get_topic_abstracts('网络爬虫', 50, 'E://')
