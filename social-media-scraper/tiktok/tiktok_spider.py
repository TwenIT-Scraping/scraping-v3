from playwright.sync_api import sync_playwright
from nested_lookup import nested_lookup
from random import randint
from datetime import datetime
import time
import json
from bs4 import BeautifulSoup


class TikTokProfileScraper(object):


    def __init__(self) -> None:
        self.credentials = {
            'username': '',
            'password': '',
            'phone_number': ''
        }

        self.hotel_page_urls = []
        self.data = {}

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False, args=['--start-maximized'])
        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()

    
    def resolve_loginform(self) -> None:
        pass

    def check_captcha(self) -> None:
        pass


    def goto_login(self) -> None:
        print('==> Go to login page')
        self.page.goto("https://www.tiktok.com/login/phone-or-email/email", timeout=40000)


    def fill_loginform(self) -> None:
        print('==> Filling login form')
        self.page.locator("//input[@type='text']").click()
        self.page.fill("//input[@type='text']", self.credentials['username'])
        time.sleep(1)
        self.page.locator("//input[@type='password']").click()
        self.page.fill("//input[@type='password']", self.credentials['username'])
        time.sleep(1)
        self.page.locator("//button[@type='submit']").click()

    def load_hotel_page(self) -> None:
        print('==> loading all establishement tiktok pages')
        self.hotel_page_urls = [
            "https://www.tiktok.com/@lacoteetlareteclaye",
            "https://www.tiktok.com/@theroxyhotelnyc",
            "https://www.tiktok.com/@modernhaussoho",
            "https://www.tiktok.com/@dreamdowntown"
        ]

    def goto_tiktok_page(self, url:str) -> None:
        print(f'==>  {url}')
        self.page.goto(url, timeout=60000)
        self.page.wait_for_timeout(25000)
        time.sleep(3)

    def extract_data(self) -> None:
        print('==> extracting data')

        def soupify(element:str) -> object:
            return BeautifulSoup(element, 'lxml')

        def extract_post() -> dict | None:
            next_post = self.page.locator("div.tiktok-1xlna7p-DivProfileWrapper.ekjxngi4").inner_html()
            element = soupify(next_post)
            date_list = element.find('span', {'data-e2e':"browser-nickname"}).find_all('span')[-1].text.split('-')
            data = {
                'title': element.find('div', {'data-e2e':"browse-video-desc"}).text.strip(),
                'publishedAt': f"{date_list[1]}/{date_list[0]}/{datetime.now().year}" if len(date_list) < 3 else f"{date_list[2]}/{date_list[1]}/{date_list[0]}",
                'likes': element.find('strong', {'data-e2e':"browse-like-count"}).text.strip(),
                'comments': element.find('strong', {'data-e2e':"browse-comment-count"}).text.strip(),
                'shares': element.find('strong', {'data-e2e':"undefined-count"}).text.strip()
            }
            return data


        header_element = self.page.locator("div.tiktok-1hfe8ic-DivShareLayoutContentV2.enm41491").inner_html()
        self.data['name'] = soupify(header_element).find('h1', {'data-e2e':'user-title'}).text.strip()
        self.data['followers'] = soupify(header_element).find('strong', {'data-e2e':'followers-count'}).text.strip()
        self.data['likes'] = soupify(header_element).find('strong', {'data-e2e':'likes-count'}).text.strip()
        self.data['establishement'] = '/api/establishment/'
        self.data['source'] = 'tiktok'
        self.data['posts'] = []

        try:
            self.page.click("div.tiktok-x6f6za-DivContainer-StyledDivContainerV2.eq741c50")
            self.page.wait_for_timeout(10000)
            self.data['posts'].append(extract_post())
            x = 0
            while self.page.locator("css=[data-e2e='arrow-right']").is_visible() and x < 20:
                self.page.click("css=[data-e2e='arrow-right']")
                self.page.wait_for_timeout(2000)
                self.data['posts'].append(extract_post())
                x += 1
        except:
            pass
    
    def save(self) -> None:
        print('==> Saving data')
        with open('./demo_tiktok.json', 'a') as openfile:
            openfile.write(json.dumps(self.data))
        self.data = {}


if __name__=='__main__':
    t = TikTokProfileScraper()
    t.goto_login()
    t.fill_loginform()
    t.load_hotel_page()
    for url in t.hotel_page_urls:
        t.goto_tiktok_page(url)
        t.extract_data()
        t.save()
        break
            