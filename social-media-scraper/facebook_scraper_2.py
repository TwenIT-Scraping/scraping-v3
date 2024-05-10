from playwright.sync_api import sync_playwright
from random import randint
from bs4 import BeautifulSoup
import time
import json
import os
from datetime import datetime, timedelta
from dateutil import parser
from scraping import Scraping
from progress.bar import ChargingBar, FillingCirclesBar
from nested_lookup import nested_lookup


class FacebookProfileScraper(Scraping):

    def __init__(self, items: list = []) -> None:
        super().__init__(items)
        self.set_credentials('facebook')

        self.hotel_page_urls = []
        self.xhr_calls = []

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False, args=['--start-maximized'])
        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()

    def stop(self):
        self.context.close()

    def create_logfile(self, logfile_name: str) -> None:
        pass

    def load_history(self) -> None:
        pass

    def set_history(self, key: str, value: any) -> None:
        pass

    def resolve_loginform(self) -> None:
        self.fill_loginform()

    def goto_login(self) -> None:
        self.page.goto("https://www.facebook.com/")
        self.page.wait_for_timeout(30000)

    def fill_loginform(self) -> None:
        self.page.wait_for_selector("[id='email']", timeout=20000)
        self.page.locator("[id='email']").click()
        time.sleep(.5)
        self.page.fill("[id='email']", self.current_credential['email'])
        time.sleep(.3)
        self.page.locator("[id='pass']").click()
        time.sleep(.2)
        self.page.fill("[id='pass']", self.current_credential['password'])
        time.sleep(.1)
        self.page.locator("[type='submit']").click()
        self.page.wait_for_timeout(20000)

    def goto_fb_page(self) -> None:
        self.page.on("response", self.intercept_response)
        self.page.goto(self.url, timeout=80000)
        self.page.wait_for_timeout(80000)
        time.sleep(.5)

    def format_values(self, data: object) -> int:
        pass

    def intercept_response(self, response) -> None:
        """capture all background requests and save them"""
        response_type = response.request.resource_type
        index = 0

        print("type: ", response_type)

        if response_type == "xhr":
            if 'graphql/' in response.url:
                try:
                    response_content = response.json()
                    print(nested_lookup(
                        key='__typename', document=response_content))
                    [print(item) for item in nested_lookup(
                        key='__typename', document=response_content)]

                    if len(has_story):
                        with open(f'content_{index}.json', 'w') as file:
                            file.write(json.dumps(response_content, indent=4))
                except:
                    pass
                # self.xhr_page = response.json()['data']['user']
            # if 'graphql' in response.url:
            #     if 'xdt_api__v1__feed__user_timeline_graphql_connection' in response.json()['data']:
            #         [self.xhr_posts.append(item) for item in response.json(
            #         )['data']['xdt_api__v1__feed__user_timeline_graphql_connection']['edges']]

            # if 'comments/' in response.url:
            #     try:
            #         self.xhr_comments.append(response.json())
            #     except Exception as e:
            #         print(e)
            #         pass

    def scoll_down_page(self) -> None:
        for i in range(5):
            self.page.evaluate(
                "window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(3000)
            time.sleep(.5)

    def get_post_count(self) -> str:
        soupe = BeautifulSoup(self.page.content(), 'lxml')
        current_post = soupe.find('div', {'class': "x9f619 x1n2onr6 x1ja2u2z xeuugli xs83m0k x1xmf6yo x1emribx x1e56ztr x1i64zmx xjl7jj x19h7ccj xu9j1y6 x7ep2pv"}).find_all(
            'div', {'x1n2onr6 x1ja2u2z'})
        return len(current_post)

    def load_page_content(self) -> None:
        self.page.on("response", self.intercept_response)
        current_post = self.get_post_count()
        new_post = 0
        while new_post != current_post:
            self.scoll_down_page()
            current_post = new_post
            new_post = self.get_post_count()
            if current_post >= 40:
                break

    def extract_data(self) -> None:
        soupe = BeautifulSoup(self.page.content(), 'lxml')
        page_name = soupe.find('div', {'class': "x1e56ztr x1xmf6yo"}).text \
            if soupe.find('div', {'class': "x1e56ztr x1xmf6yo"}) else ''
        page_likes = soupe.find_all('a', {'class': "x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1s688f"})[0].text.strip() \
            if soupe.find_all('a', {'class': "x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1s688f"}) else 0

        page_likes = self.format_string_number(page_likes)
        print(page_likes)

        page_followers = soupe.find_all('a', {'class': "x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1s688f"})[1].text.strip() \
            if soupe.find_all('a', {'class': "x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1s688f"}) else 0

        page_followers = self.format_string_number(page_followers)

        self.page_data = {
            'name': f"fb_{page_name}",
            'likes': int(''.join(filter(str.isdigit, page_likes))),
            'followers': int(''.join(filter(str.isdigit, page_followers))),
            'source': 'facebook',
            'establishment': self.establishment,
            'posts': len(self.posts)
        }

    def switch_acount(self) -> None:
        pass

    def execute(self) -> None:
        progress = ChargingBar('Preparing ', max=3)
        self.set_current_credential(1)
        progress.next()
        print(" | Open login page")
        self.goto_login()
        progress.next()
        print(" | Fill login page")
        self.fill_loginform()
        progress.next()
        print(" | Logged in!")
        progress = ChargingBar('Processing ', max=len(self.items))
        for item in self.items:
            # p_item = FillingCirclesBar(item['establishment_name'], max=5)
            try:
                self.set_item(item)
                # p_item.next()
                print(" | Open page")
                self.goto_fb_page()
                # p_item.next()
                print(" | Load content page")
                self.load_page_content()
                # p_item.next()
                # print(" | Extracting")
                # self.extract_data()
                # p_item.next()
                # print(" | Saving")
                # self.save()
                # p_item.next()
                # print(" | Saved")
            except:
                pass
            progress.next()
        self.stop()
