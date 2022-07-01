from telnetlib import EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pds

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np
import time
import re
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from datetime import datetime
import json


id_list = []

## 01. 웹 열기
driver = webdriver.Chrome(ChromeDriverManager().install()) #웹드라이버로 크롬 웹 켜기
driver.set_window_size(800, 1200) 	#브라우저 크기 800*1200으로 고정
driver.get('https://www.instagram.com/') #인스타그램 웹 켜기
time.sleep(2) 	#2초 대기



## 02. 로그인
#경로 지정
id_box = driver.find_element_by_css_selector("#loginForm > div > div:nth-child(1) > div > label > input")   #아이디 입력창
password_box = driver.find_element_by_css_selector("#loginForm > div > div:nth-child(2) > div > label > input")     #비밀번호 입력창
login_button = driver.find_element_by_css_selector('#loginForm > div > div:nth-child(3) > button')      #로그인 버튼

#동작 제어
act = ActionChains(driver)      #동작 명령어 지정
act.send_keys_to_element(id_box, 'hwany_01').send_keys_to_element(password_box, 'ghksl01!').click(login_button).perform()     #아이디 입력, 비밀 번호 입력, 로그인 버튼 클릭 수행
time.sleep(2)
 
## 03. 해시태그 검색
hashtag = str(input("Search for the hashtag: "))
tagUrl = "http://www.instagram.com/explore/tags/" + str(hashtag)
driver.get(tagUrl)
time.sleep(10)

first_post = driver.find_element(By.CSS_SELECTOR, 'div._aagu')
first_post.click()
time.sleep(5)

for i in range(9):
    #n_post = f'//*[@id="mount_0_0_3r"]/div/div[1]/div/div[1]/div/div/div[1]/div[1]/section/main/article/div[1]/div/div/div[1]/div[1]'
    #//*[@id="mount_0_0_S+"]/div/div[1]/div/div[1]/div/div/div[1]/div[1]/section/main/article/div[1]/div/div/div[1]/div[2]/a/div[1]/div[2]
    #//*[@id="mount_0_0_Q9"]/div/div[1]/div/div[1]/div/div/div[1]/div[1]/section/main/article/div[1]/div/div/div[1]/div[2]/a

    user_name = driver.find_element(By.CSS_SELECTOR, 'div._aaqt')
    print(user_name.text)
    id_list.append(user_name.text)
    time.sleep(3)
    #next_btn_css = 'div._'
    #WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, next_btn_css))
    next_btn = driver.find_element(By.CSS_SELECTOR, 'div._aaqg._aaqh')
    next_btn.click()
    time.sleep(5)
    

print(id_list)

for j in id_list:

    #profile = driver.current_url    
    profile = "http://www.instagram.com/" + j
    driver.get(profile)
    time.sleep(5)
    
    ## 04. 계정주 정보 수집

    r = requests.get(profile, params={"__a": 1, "__d": "dis"})  # requests로 GET 요청 보냄, params 파라미터로 path parameter 넣을 수 있음.

    # 반환된 JSON 데이터(r)을 .json() 메소드로 파이썬에서 사용할 수 있는 dict 형식으로 변경


    # 반환 데이터에서 "graphql"키와 "user"키에서 유저 데이터를 담고 있는것을 확인하였으므로 변수에 저장함
    user_data = r.json()["graphql"]["user"]

    engine_category = r.json()["seo_category_infos"]

    # dict에서 필요한 데이터 가져옴
    intro = user_data["biography"]
    name = user_data["full_name"]
    follower = user_data["edge_followed_by"]["count"]
    following = user_data["edge_follow"]["count"]

    print(engine_category)
    print(intro)
    print(name)
    print(follower)
    print(following)



'''
class Instagram:
    def __init__(self):
        self.csrf_token = ""
        self.session_id = ""
        self.headers = {}
        self.cookies = {}

        self.sess = None
    
    def login(self, username, password):
        link = 'https://www.instagram.com/accounts/login/'
        login_url = 'https://www.instagram.com/accounts/login/ajax/'

        self.sess = requests.session()

        time = int(datetime.now().timestamp())
        response = self.sess.get(link)
        csrf = response.cookies['csrftoken']

        payload = {
            'username': username,
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{time}:{password}',
            'queryParams': {},
            'optIntoOneTap': 'false'
        }

        self.headers = {
            # "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/login/",
            "x-csrftoken": csrf
        }

        login_response = self.sess.post(login_url, data=payload, headers=self.headers)
        json_data = json.loads(login_response.text)

        print(login_response.status_code, login_response.text)

        if json_data["authenticated"]:
            self.cookies = login_response.cookies
            # cookie_jar = self.cookies.get_dict()
            # csrf_token = cookie_jar['csrftoken']
            # session_id = cookie_jar['sessionid']
        else:
            print("login failed ", login_response.text)

    def get_search_data_tag_name(self, tag_name):
        url = "https://i.instagram.com/api/v1/tags/web_info"

        print(self.headers)
        print(self.cookies)

        r = self.sess.get(
            url,
            headers=self.headers,
            cookies=self.cookies,
            params={
                "tag_name": tag_name
            }
        )

        print(r.text)


username = "hwany_01"
password = "rlaehdghks01!"

instagram = Instagram()
instagram.login(username, password)
instagram.get_search_data_tag_name("캠핑")'''