#!/usr/bin/env python
# coding: utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import requests
from fake_useragent import UserAgent
import os
import math
import pymongo
# 開啟webdriver權限
os.chmod('chromedriver_win32/', 755)

# 建立DB連線
db_connect = pymongo.MongoClient('mongodb://localhost:27017/')
db = db_connect['591_crawler']


def get_item_inf(url):
    # 先看網址是否導向成功
    itme_user_agent = UserAgent()  # 用fake_useragent在每次Request前，隨機產生使用者代理
    res_item=requests.get(url, headers={ 'user-agent': itme_user_agent.random })
    if res_item.status_code == 200 :
        browser_item = webdriver.Chrome('chromedriver_win32/chromedriver.exe')
        browser_item.get(url)
        time.sleep(3)
        item_page_sp = BeautifulSoup(browser_item.page_source, 'html.parser')

        temp_inf_ls = [] # 暫存只會擷取其中幾個資訊的LS
        for i in item_page_sp.find('div', {'class':'house-pattern'}):
            if i.text :
                temp_inf_ls.append(i.text)

        item_shape = temp_inf_ls[-1] # 型態:公寓/電梯大樓
        del temp_inf_ls[:] # 暫存清空

        # GET Tel
        if item_page_sp.find('span', 'tel-txt') :
            for i in item_page_sp.select('div.reference > span.tel-txt'):
                if i.text :
                    temp_inf_ls.append(i.text)
            item_tel = temp_inf_ls[-1] # tel
            del temp_inf_ls[:] # 暫存清空
        else :
            item_tel = '無'

        browser_item.close()
        return item_tel, item_shape
    else :
        return '404錯誤', '404錯誤'



def get_591_item(local, gender):
    # ex. 台北市出租物件:https://rent.591.com.tw/?kind=0&region=1
    local_dict = {
        '台北市': '&region=1',
        '新北市': '&region=3'
    }

    # ex.台北市限租女物件:https://rent.591.com.tw/?kind=0&region=1&multiNotice=girl&showMore=1
    gender_dict = {
        '男女皆可': '&multiNotice=all_sex',
        '限男': '&multiNotice=boy',
        '限女': '&multiNotice=girl'
    }

    url = 'https://rent.591.com.tw/?kind=0%s%s&showMore=1' % (local_dict[local], gender_dict[gender])
    
    # 先看網址是否導向成功(status_code == 200 )
    user_agent = UserAgent()  # 用fake_useragent在每次Request前，隨機產生使用者代理
    res=requests.get(url, headers={ 'user-agent': user_agent.random })
    if res.status_code == 200 :
        ## Setup SOUP
        browser = webdriver.Chrome('chromedriver_win32/chromedriver.exe')
        browser.get(url)
        time.sleep(3)
        soup = BeautifulSoup(browser.page_source, 'html.parser')

        # 取總頁數：一頁預設顯示30物件，除不盡將無條件進位
        page_length = math.ceil(int(soup.find('span', 'TotalRecord').text.split(' ')[1])/30)
        
        for p in range(page_length) :
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            current_page_list = soup.find_all('section', 'vue-list-rent-item')
            ## 取當前頁面的30個URL、物件名稱、出租者與身分
            # 遍歷整頁的30個物件，利用其連結獲得裡頭資訊，另外也存放標題名稱
            for i in current_page_list :
                if i.find('a'):

                    # 取物件URL
                    item_url = i.find('a')['href']

                    # 取物件名稱ex.'內湖站全新設計裝潢2房2廳+陽台'
                    item_title = i.find('div', 'item-title').text.strip().split('\n')[0]

                    # 取屋主資訊
                    renter = i.find('div', 'item-msg').text.strip().split()[1] # 屋主名字:X小姐/先生
                    renter_id = i.find('div', 'item-msg').text.strip().split()[0] # 身分:屋主

                    # 取物件類型/現況(kind)
                    kind = i.find('ul' ,'item-style').text.strip().split()[0]

                    # 取連結內資訊
                    # 若出租類型/現況(kind)為"車位"則無型態資料
                    tel, shape = get_item_inf(item_url)
                    if kind == '車位' :
                        shape = '無'
                    data_info = {
                        '地區': local, 
                        '性別要求': gender, 
                        '物件名稱': item_title, 
                        '出租者': renter, 
                        '出租者身分': renter_id, 
                        '聯絡電話': tel, 
                        '型態(Shape)': shape, 
                        '現況(Kind)': kind, 
                        'URL': item_url
                    }
                    # 插入新資料到mongoDB集合
                    db_sites.insert_one(data_info)


            # 換頁條件:如果到了最後一頁，下一頁按鈕class變成pageNext last，就不進行換頁
            if soup.find('a', 'pageNext last'):
                browser.close()
            else :
                browser.find_element_by_class_name('pageNext').click()
                time.sleep(3)

    else :
        print('未成功導向指定網頁')



if __name__ == '__main__':

    # 先設定存入的集合，再設定地區與性別設定後開始爬蟲
    db_sites = db['item']
    get_591_item('台北市', '男女皆可')
    time.sleep(3)
    get_591_item('台北市', '限男')
    time.sleep(3)
    get_591_item('台北市', '限女')
    time.sleep(3)
    get_591_item('新北市', '男女皆可')
    time.sleep(3)
    get_591_item('新北市', '限女')
    time.sleep(3)
    get_591_item('新北市', '限男')

    # 關閉連線
    db_connect.close()
