from playwright.sync_api import sync_playwright
from random import randint
from bs4 import BeautifulSoup
import time
import json
import os
from datetime import datetime, timedelta
from dateutil import parser
from scraping import Scraping


class FacebookProfileScraper(Scraping):

    def __init__(self, items: list = []) -> None:
        print('==> initializing facebook scraper ...')
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
        print('==> resolving login form ...')
        self.fill_loginform()

    def goto_login(self) -> None:
        print('==> logging In ...')
        self.page.goto("https://www.facebook.com/")
        self.page.wait_for_timeout(30000)

    def log_out(self) -> None:
        print('==> logout ...')

    def fill_loginform(self) -> None:
        print('==> filling login form ...')
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
        print('==> submitted ...')
        self.page.wait_for_timeout(20000)

    def goto_fb_page(self) -> None:
        print(self.url)
        self.page.goto(self.url, timeout=80000)
        self.page.wait_for_timeout(80000)
        time.sleep(.5)

    def format_values(self, data: object) -> int:
        pass

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
        # self.scoll_down_page()
        # self.extract_data()
        current_post = self.get_post_count()
        new_post = 0
        while new_post != current_post:
            self.scoll_down_page()
            current_post = new_post
            new_post = self.get_post_count()
            print('current_post', current_post)
            print('new_post', new_post)
            # self.extract_data()
            if current_post >= 40:
                break

    def format_date(self, date):
        print(date)
        dt = date.split()
        day = None
        month = datetime.now().month
        year = datetime.now().year

        print(dt)

        if dt[0][len(dt[0])-1] == 'h' and dt[0][:-1].isnumeric():
            time = datetime.now() + timedelta(hours=-(int(dt[0][:-1])))
            day = time.day
            month = time.month
            year = time.year

        elif dt[0][len(dt[0])-1] == 'd' and dt[0][:-1].isnumeric():
            time = datetime.now() + timedelta(days=-(int(dt[0][:-1])))
            day = time.day
            month = time.month
            year = time.year

        else:
            d = parser.parse(date)

            return d.strftime('%Y/%m/%d')

        return f"{year}/{month}/{day}"

    def format_string_number(self, value):
        first_value = 0
        second_value = 0
        value = value.lower()
        try:
            if 'm' in value:
                first_value = int(value.split(',')[0]) * 1000000
                second_value = int(
                    ''.join(filter(str.isdigit, value.split(',')[1]))) * 100000
            if 'k' in value:
                first_value = int(value.split(',')[0]) * 1000
                second_value = int(
                    ''.join(filter(str.isdigit, value.split(',')[1]))) * 100
            else:
                first_value = int(''.join(filter(str.isdigit, value)))
        except Exception as e:
            print(e)
            pass

        return str(first_value + second_value)

    def extract_data(self) -> None:
        soupe = BeautifulSoup(self.page.content(), 'lxml')
        page_name = soupe.find('div', {'class': "x1e56ztr x1xmf6yo"}).text \
            if soupe.find('div', {'class': "x1e56ztr x1xmf6yo"}) else ''
        page_likes = soupe.find_all('a', {'class': "x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1s688f"})[0].text.strip() \
            if soupe.find_all('a', {'class': "x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1s688f"}) else 0
        page_likes = self.format_string_number(page_likes)

        page_followers = soupe.find_all('a', {'class': "x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1s688f"})[1].text.strip() \
            if soupe.find_all('a', {'class': "x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1s688f"}) else 0
        page_followers = self.format_string_number(page_followers)
        post_container = soupe.find('div', {
                                    'class': "x9f619 x1n2onr6 x1ja2u2z xeuugli xs83m0k x1xmf6yo x1emribx x1e56ztr x1i64zmx xjl7jj x19h7ccj xu9j1y6 x7ep2pv"})
        post_data = post_container.find_all('div', {'x1n2onr6 x1ja2u2z'})
        print(len(post_data))
        for post in post_data:
            try:
                likes = post.find('span', {'class': "xt0b8zv x2bj2ny xrbpyxo xl423tq"}).text.strip() \
                    if post.find('span', {'class': "xt0b8zv x2bj2ny xrbpyxo xl423tq"}) else '0'
                likes = self.format_string_number(likes)
                description = post.find('div', {'class': "xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs x126k92a"}).text.strip() \
                    if post.find('div', {'class': "xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs x126k92a"}) else ''
                cs = post.find('div', {
                    'class': "x9f619 x1n2onr6 x1ja2u2z x78zum5 x2lah0s x1qughib x1qjc9v5 xozqiw3 x1q0g3np xykv574 xbmpl8g x4cne27 xifccgj"})
                comments = 0
                shares = 0
                if cs and cs.text:
                    c = cs.find_all('span', {'dir': 'auto'})
                    match(len(c)):
                        case 2:
                            shares = self.format_string_number(c[1].text.lower().replace('shares', '').replace(
                                'share', '').strip())
                            shares = int(''.join(filter(str.isdigit, shares)))
                            comments = self.format_string_number(c[0].text.lower().replace('comment', '').replace(
                                'comments', '').strip())
                            comments = int(
                                ''.join(filter(str.isdigit, comments)))
                        case 1:
                            if 'share' in c[0].text or 'shares' in c[0].text:
                                shares = self.format_string_number(c[0].text.lower().replace('shares', '').replace(
                                    'share', '').strip())
                                shares = int(
                                    ''.join(filter(str.isdigit, shares)))
                            if 'comment' in c[0].text or 'comments' in c[0].text:
                                comments = self.format_string_number(c[0].text.lower().replace('comment', '').replace(
                                    'comments', '').strip())
                                comments = int(
                                    ''.join(filter(str.isdigit, comments)))
                        case _:
                            shares = 0
                            comments = 0

                # spans_date = post.find(
                #     'span', {'id': ':Rlataul9l9aqqd9emhpapd5aqH1:'}).text.strip()
                # print(spans_date)

                # print(
                #     post.find('object', {'type': 'nested/pressable'}).find('a').text.strip())

                item = {
                    'title': "",
                    'reaction': int(''.join(filter(str.isdigit, likes))),
                    'description': description,
                    'comments': comments,
                    'share': shares,
                    # 'date': self.format_date(date)
                    'uploadAt': '2023-08-11'
                }
                # print(item)
                self.posts.append(item)
            except Exception as e:
                print(e)
                pass

        self.page_data = {
            'name': f"fb_{page_name}",
            'likes': int(''.join(filter(str.isdigit, page_likes))),
            'followers': int(''.join(filter(str.isdigit, page_followers))),
            'source': 'facebook',
            'establishment': f"/api/establishment/{self.establishment}",
            'posts': len(self.posts)
        }

    # def save(self, data: dict) -> None:
    #     print('==> saving data ...')
    #     dict_data = json.dumps(data, indent=4)
    #     with open('demo.json', 'a') as openfile:
    #         openfile.write(dict_data)
    #     data.clear()

    def switch_acount(self) -> None:
        pass

    def execute(self) -> None:
        self.set_current_credential(1)
        self.goto_login()
        self.fill_loginform()
        for item in self.items:
            try:
                print("Itérer ...")
                self.set_item(item)
                self.goto_fb_page()
                self.load_page_content()
                self.extract_data()
                self.save()
            except:
                pass
        self.stop()
