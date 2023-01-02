from numpy import outer
import requests
from datetime import datetime
import json
import pandas as pd
import time
from tqdm import tqdm
import re
from sqlalchemy import create_engine
import os

#load_dotenv()

df = pd.read_excel("usernames.xlsx", names=['id'])

account_list = df.values.tolist()

insert_account_list = []

comment_list = []

'''engine = create_engine(f"mysql+pymysql://{os.getenv('dbus')}:{os.getenv('dbpw')}@{os.getenv('dbip')}/{os.getenv('dbnm')}")

conn = engine.connect()

raw_info = pd.read_sql("SELECT * FROM RawInfo;",conn)
id_list = raw_info['Username'].to_list()
print(id_list)'''


# 인스타그램의 API는 로그인 정보가 필요하므로
# 먼저 로그인을 진행한 후 사용
class Instagram:
    def __init__(self):  # 로그인 실행 시 값들이 채워짐
        self.csrf_token = ""
        self.session_id = ""
        self.headers = {}
        self.cookies = {}

        self.sess = None  # 로그인 유지를 위해 requests의 session 클래스를 사용

    def login(self, username, password):  # 인스타그램 로그인
        link = 'https://www.instagram.com/api/v1/web/accounts/login/ajax/'
        login_url = 'https://www.instagram.com/api/v1/web/accounts/login/ajax/'

        self.sess = requests.session()

        time = int(datetime.now().timestamp())
        response = self.sess.get(link) #로그인 링크에 대한 세션을 반환
        csrf = response.cookies['csrftoken']

        payload = {
            'username': username,
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{time}:{password}',
            'queryParams': {},
            'optIntoOneTap': 'false'
        }

        self.headers = {#로그인시 전송해야할 헤더값들을 설정
            # "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
            # 특정 User-Agent를 사용하지 않으면 에러를 반환
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/login/",
            "x-csrftoken": csrf
        } 

        login_response = self.sess.post(login_url, data=payload, headers=self.headers) #로그인 api에 parameter들을 post
        json_data = json.loads(login_response.text)

        print(login_response.status_code, login_response.text)

        # 토큰 등 로그인 정보를 받아온 후 cookies 변수에 저장
        if json_data["authenticated"]:
            self.cookies = login_response.cookies
        else:
            print("login failed ", login_response.text)

    def get_search_data_tag_name(self, tag_name):  # 해쉬태그를 검색하여 나오는 게시물 정보
        url = "https://i.instagram.com/api/v1/tags/web_info"

        r = self.sess.get(
            url,
            headers=self.headers,
            cookies=self.cookies,
            params={
                "tag_name": tag_name
            }
        )

        return r.json()["data"]  # ["top"]["sections"]

    def get_top_search_tag(self, tag_name):  # 인스타그램 검색창에 입력 시 실행되는 api, 추천 검색어를 반환함
        url = "https://www.instagram.com/web/search/topsearch/"

        r = self.sess.get(
            url,
            headers=self.headers,
            cookies=self.cookies,
            params={
                "context": "blended",
                "query": tag_name,
                "include_reel": "true"
            }
        )

        return r.json()["hashtags"]

    def get_user_info(self, user_id):  # 단일 계정에 대한 팔로워 수를 반환
        url = "https://i.instagram.com/api/v1/users/web_profile_info"

        r = self.sess.get(
            url,
            headers=self.headers,
            cookies=self.cookies,
            params={
                "username": user_id
            }
        )

        return r.json()["data"]

    def get_comment(self, medium_id):
        url = "https://i.instagram.com/api/v1/media/" + medium_id + "/comments"

        r = self.sess.get(
            url,
            headers=self.headers,
            cookies=self.cookies,
            params={
                "can_support_threading": "true",
                "permalink_enabled": "false"
            }
        )
        return r.json()["comments"]



## id, pw를 입력해주세요.
username = ""
password = ""

instagram = Instagram()
instagram.login(username, password)


#print(account_list)

for account in tqdm(account_list, desc="getting userinfo"):
    try:
        time.sleep(30)
        individual_info_list = []
        account_info = instagram.get_user_info(account) # 하나의 account 정보 반환

        mediatext = ""
        media_id = []
        commenttext = ""
        timestamp_list = []

        media_list = account_info["user"]["edge_owner_to_timeline_media"]["edges"] # 하나의 account 정보 중 게시물이 들어있는 곳

        for medium in media_list: # 하나의 account에 대한 계시물 고유 id 리스트 생성
            media_id.append(medium["node"]["id"])

        for medium_id in media_id: # 하나의 account에 대한 계시물 고유 id 리스트 생성
            time.sleep(30)
            comments = instagram.get_comment(medium_id)  
            for comment in comments:
                commenttext += comment["text"]
                print(comment["text"])
        comment_list.append(commenttext)

        insert_account_list.append(account)
    except Exception as e:
        print(e)


column = ['댓글']
df = pd.DataFrame(comment_list, columns=column)
#print(insert_account_list)

df.insert(0, "account_id", insert_account_list, True)
df.drop_duplicates(ignore_index=True, inplace=True)
print(df)

df.to_excel("댓글.xlsx")
