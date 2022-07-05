import requests
from datetime import datetime
import json
import pandas as pd

#초기 검색 해시태그
searching_tag_list = ["#골프웨어", "#캠핑", "#요리", "#화장품"]# "#공구", "#광고", "#협찬", "#캠핑", "#골프", "#요리", "#뷰티", "#육아", "#맛집", "#육아", "#요리", "#데일리룩", "#ootd", "#운동", "#직장인", "#다이어트", "#테니스", "#라이딩", "#댕댕이", "#화장품", "#산책", "#발색", "#카페", "#분위기", "#일상", "#오늘", "#여친", "#남친", "#커플", "#데이트", "#가족", "#먹방", "#서울", "#호캉스", "#아이폰", "#차박", "#자동차", "#호텔", "#책", "#영화", "#주방"]

#초기 검색 해시태그로부터 얻는 추천 해시태그
recommend_tag_list = []

#계정명
account_list = []

#계정정보
account_info_list = []


# 인스타그램의 API는 로그인 정보가 필요하므로
# 먼저 로그인을 진행한 후 사용
class Instagram:
    def __init__(self): #로그인 시 값들이 채워짐
        self.csrf_token = "" 
        self.session_id = ""
        self.headers = {}
        self.cookies = {}

        self.sess = None # 로그인 유지를 위해 requests의 session 클래스를 사용

    def login(self, username, password): # 인스타그램 로그인
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
            # 특정 User-Agent를 사용하지 않으면 에러를 반환
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/login/",
            "x-csrftoken": csrf
        }

        login_response = self.sess.post(login_url, data=payload, headers=self.headers)
        json_data = json.loads(login_response.text)

        print(login_response.status_code, login_response.text)

        # 토큰 등 로그인 정보를 받아온 후 cookies 변수에 저장
        if json_data["authenticated"]:
            self.cookies = login_response.cookies
        else:
            print("login failed ", login_response.text)

    def get_search_data_tag_name(self, tag_name): # 해쉬태그를 검색하여 나오는 게시물 정보
        url = "https://i.instagram.com/api/v1/tags/web_info"

        r = self.sess.get(
            url,
            headers=self.headers,
            cookies=self.cookies,
            params={
                "tag_name": tag_name
            }
        )

        return r.json()["data"]["top"]["sections"]

    def get_top_search_tag(self, tag_name): # 인스타그램 검색창에 입력 시 실행되는 api, 추천 검색어를 반환함
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

    def get_user_info(self, user_id): #단일 계정에 대한 팔로워 수를 반환
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


username = ""
password = ""

instagram = Instagram()
instagram.login(username, password)

#전체 구현을 위한 bits
'''tags = instagram.get_top_search_tag("#여행")
outer_hashtag_id = instagram.get_search_data_tag_name("겨울")
account_info = instagram.get_user_info("skku_spring__nsc")

#단일 태그에 대한 추천 태그 리스트
for tag in tags:
    this_tag = tag["hashtag"]["name"]
    recommend_tag_list.append(this_tag)
    #print(this_tag)

#단일 태그에 대한 게시물 작성자 id 리스트
for row in outer_hashtag_id:
    inner_hashtag_id = row["layout_content"]["medias"]

    for point in inner_hashtag_id:
        point_id = point["media"]["user"]["username"]
        account_list.append(point_id)

#단일 계정의 팔로워, 팔로잉 수
followers = account_info["user"]["edge_followed_by"]["count"]
following = account_info["user"]["edge_follow"]["count"]

#단일 계정의 최근 12게시물 평균 좋아요 수
like = 0
media_list = account_info["user"]["edge_owner_to_timeline_media"]["edges"]
for medium in media_list:
        like += medium["node"]["edge_liked_by"]["count"]

avg_like = like / 12


account_info_list.append(followers)
account_info_list.append(following)
account_info_list.append(avg_like)

print(recommend_tag_list)
print(account_list)
print(avg_like)
print(followers)
print(following)'''

#초기 검색 해시태그 리스트로 추천 해시태그 리스트 생성
for searching_tag in searching_tag_list:
    tags = instagram.get_top_search_tag(searching_tag)
    for tag in tags:
        this_tag = tag["hashtag"]["name"]
        recommend_tag_list.append(this_tag)

print(recommend_tag_list)

#추천 해시태그 리스트로 계정명 리스트 생성
for recommend_tag in recommend_tag_list:
    outer_hashtag_id = instagram.get_search_data_tag_name(recommend_tag)

    for row in outer_hashtag_id:
        inner_hashtag_id = row["layout_content"]["medias"]

        for point in inner_hashtag_id:
            point_id = point["media"]["user"]["username"]
            account_list.append(point_id)
            #print(point_id)

print(account_list)

#테스트(추천 해시태그 중 5개만 사용)
'''for i in range(5):
    outer_hashtag_id = instagram.get_search_data_tag_name(recommend_tag_list[i])

    for row in outer_hashtag_id:
        inner_hashtag_id = row["layout_content"]["medias"]

        for point in inner_hashtag_id:
            point_id = point["media"]["user"]["username"]
            account_list.append(point_id)
            print(point_id)'''

#계정명 리스트로 계정정보 리스트 생성
for account in account_list:
    individual_info_list = [] 
    account_info = instagram.get_user_info(account)
    
    followers = account_info["user"]["edge_followed_by"]["count"]
    following = account_info["user"]["edge_follow"]["count"]
    individual_info_list.append(followers)
    individual_info_list.append(following)

    like = 0
    media_list = account_info["user"]["edge_owner_to_timeline_media"]["edges"]
    for medium in media_list:
        like += medium["node"]["edge_liked_by"]["count"]

    avg_like = like / 12 
    individual_info_list.append(avg_like)
    
    print(individual_info_list)
    account_info_list.append(individual_info_list)




column = ['팔로잉', '팔로워', '평균 좋아요']
df = pd.DataFrame(account_info_list, columns = column)

df.insert(0, "account_id", account_list, True)
df.drop_duplicates(ignore_index=True)
print(df)

df.to_excel("data.xlsx")



