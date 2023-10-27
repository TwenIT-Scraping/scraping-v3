from playwright.sync_api import sync_playwright
from nested_lookup import nested_lookup
from random import randint
import time
import json
from datetime import datetime

class InstagramProfileScraper(object):

    def __init__(self) -> None:
        print('==> initializing twitter scraper ...')
        self.credentials = {
            'username': 'thierry0keller@gmail.com',
            'password': 'ztDCxfoAdGSHgp',
            'phone_number': '0340851090'
        }
        self.hotel_page_urls = []
        self.xhr_calls = {}
        self.data_container = {}
        self.data = []

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False, args=['--start-maximized'])
        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()

    def create_logfile(self, logfile_name:str) -> None:
        pass

    def load_history(self) -> None:
        pass

    def set_history(self, key:str, value:any) -> None:
        pass

    def resolve_loginform(self) -> None:
        print('==> resolving login form ...')
        self.fill_loginform()
        

    def goto_login(self) -> None:
        print('==> logging In ...')
        self.page.goto("https://www.instagram.com/accounts/login/", timeout=30000)

    def log_out(self) -> None:
        print('==> logout ...')
        

    def fill_loginform(self) -> None:
        print('==> filling login form ...')
        self.page.wait_for_selector("[name='username']", timeout=60000)
        self.page.locator("[name='username']").click()
        time.sleep(.5)
        self.page.fill("[name='username']", self.credentials['phone_number'])
        time.sleep(.3)
        self.page.locator("[name='password']").click()
        time.sleep(.2)
        self.page.fill("[name='password']", self.credentials['password'])
        time.sleep(.1)
        self.page.locator("[type='submit']").click()
        print('==> submitted ...')
        self.page.wait_for_timeout(70000)

    def load_hotel_pages(self) -> None:
        print('==> loading all hotels twitter pages ...')
        self.hotel_page_urls = [
            "https://www.instagram.com/lidolacdubourget/?hl=en",
            "https://www.instagram.com/thechelseapinesinn/?hl=en",
            "https://www.instagram.com/dreamdowntown/?hl=en",
            "https://www.instagram.com/thedominickhotel/?hl=en",
            "https://www.instagram.com/theroxyhotelnyc/?hl=en"
            "https://www.instagram.com/hyattunionsqnyc/?hl=en",
            "https://www.instagram.com/thechelseapinesinn/?hl=en",
            "https://www.instagram.com/nobledenhotel/?hl=en",
        ]


    def intercept_response(self, response) -> None:
        """capture all background requests and save them"""
        response_type = response.request.resource_type
        if response_type == "xhr":
            with open('xhr.txt', 'a') as file:
                file.write(response.json())
            if 'username' in response.url:
                self.xhr_calls = response.json()
    
    def goto_insta_page(self, url:str) -> None:
        self.page.on("response", self.intercept_response)
        self.page.goto(url)
        self.page.wait_for_timeout(60000)
        time.sleep(3)

    def get_json_content(self, item:object, key:str) -> object:
        try:
            return item[key]
        except KeyError:
            return ''

    def extract_data(self) -> dict:
        pass
        # with open('demo.json', 'w') as file:
        #     file.write(json.dumps(self.xhr_calls, indent=4))
        # self.data_container = {
        #     # "biorgraphy": nested_lookup(key='biography', document=self.xhr_calls)[0] if nested_lookup(key='biography', document=self.xhr_calls)[0] else '',
        #     "followers": nested_lookup(key='edge_followed_by', document=self.xhr_calls)[0]['count'],
        #     # "following": nested_lookup(key='edge_follow', document=self.xhr_calls)[0]['count'],
        #     "name": nested_lookup(key='full_name', document=self.xhr_calls)[0],
        #     # "posts_count": nested_lookup(key='edge_owner_to_timeline_media', document=self.xhr_calls)[0]['count'],
        #     "posts": []
        # }

        # all_posts = nested_lookup(key='edge_felix_video_timeline', document=self.xhr_calls)[0]['edges']
        # for post in all_posts:
        #     self.data_container['posts'].append({
        #             "source": "instagram",
        #             "publishedAt": datetime.fromtimestamp(nested_lookup(key='taken_at_timestamp', document=post)[0]).strftime("%d/%m/%Y"),
        #             "title": nested_lookup(key='text', document=post)[0],
        #             "comments": nested_lookup(key='edge_media_to_comment', document=post)[0]['count'],
        #             "likes": nested_lookup(key='edge_liked_by', document=post)[0]['count']
        #         })

        # other_posts = nested_lookup(key='edge_owner_to_timeline_media', document=self.xhr_calls)[0]['edges']
        # for other_post in other_posts:
        #     post_text = nested_lookup(key='node', document=other_post['node'])[0]
        #     self.data_container['posts'].append({
        #             "source": "instagram",
        #             "publishedAt": datetime.fromtimestamp(nested_lookup(key='taken_at_timestamp', document=other_post)[0]).strftime("%d/%m/%Y"),
        #             "title": post_text['text'] if type(post_text) == str else '',
        #             "comments": nested_lookup(key='edge_media_to_comment', document=other_post)[0]['count'],
        #             "likes": nested_lookup(key='edge_liked_by', document=other_post)[0]['count']
        #         })
        # self.data.append(self.data_container)

    def save(self) -> None:
        print('==> saving data ...')
        with open('instagram.json', 'w') as openfile:
            openfile.write(json.dumps(self.data))

    def switch_acount(self) -> None:
        pass

if __name__=='__main__':
    print("==> program is lauching ('_')")
    t = InstagramProfileScraper()
    t.goto_login()
    t.fill_loginform()
    t.load_hotel_pages()
    for url in t.hotel_page_urls:
        t.goto_insta_page(url=url)
        t.extract_data()
        t.save()
    print("==> program finished ('_')")
    
