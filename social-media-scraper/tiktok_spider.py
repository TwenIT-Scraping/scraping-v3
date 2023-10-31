from playwright.sync_api import sync_playwright
from nested_lookup import nested_lookup
from random import randint
from datetime import datetime
import time
import json
from bs4 import BeautifulSoup
from scraping import Scraping
from dateutil.relativedelta import relativedelta


class TikTokProfileScraper(Scraping):

    def __init__(self, items: list = []) -> None:
        super().__init__(items)
        # self.set_credentials('tiktok')

        self.hotel_page_urls = []
        self.data = {}

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False, args=['--start-maximized'])
        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()

    def stop(self):
        self.context.close()

    def resolve_loginform(self) -> None:
        pass

    def check_captcha(self) -> None:
        pass

    def goto_login(self) -> None:
        print('==> Go to login page')
        self.page.goto(
            "https://www.tiktok.com/login/phone-or-email/email", timeout=40000)

    def fill_loginform(self) -> None:
        print('==> Filling login form')
        self.page.locator("//input[@type='text']").click()
        self.page.fill("//input[@type='text']",
                       self.current_credential['email'])
        time.sleep(1)
        self.page.locator("//input[@type='password']").click()
        self.page.fill("//input[@type='password']",
                       self.current_credential['password'])
        time.sleep(1)
        self.page.locator("//button[@type='submit']").click()

    def goto_tiktok_page(self) -> None:
        print(f'==>  {self.url}')
        self.page.goto(self.url, timeout=100000)
        self.page.wait_for_timeout(25000)
        time.sleep(3)

    def extract_data(self) -> None:
        print('==> extracting data')

        def soupify(element: str) -> object:
            return BeautifulSoup(element, 'lxml')

        def extract_post() -> dict | None:
            next_post = self.page.locator(
                "div.tiktok-1xlna7p-DivProfileWrapper.ekjxngi4").inner_html()
            element = soupify(next_post)

            date_list = element.find(
                'span', {'data-e2e': "browser-nickname"}).find_all('span')[-1].text.split('-')

            if len(date_list) == 3:
                publishedAt = f"{date_list[2]}/{date_list[1]}/{date_list[0]}"
            elif len(date_list) == 2:
                publishedAt = f"{date_list[1]}/{date_list[0]}/{datetime.now().year}"
            else:
                day = int(''.join(filter(str.isdigit, date_list[0])))
                publishedAt = (datetime.now(
                ) - relativedelta(days=day)).strftime("%d/%m/%Y")

            data = {
                'title': element.find('div', {'data-e2e': "browse-video-desc"}).text.strip(),
                'publishedAt': publishedAt,
                'likes': element.find('strong', {'data-e2e': "browse-like-count"}).text.strip(),
                'comments': element.find('strong', {'data-e2e': "browse-comment-count"}).text.strip(),
                'shares': element.find('strong', {'data-e2e': "undefined-count"}).text.strip()
            }
            return data

        header_element = self.page.locator(
            "div.tiktok-1hfe8ic-DivShareLayoutContentV2.enm41491").inner_html()
        self.page_data['name'] = soupify(header_element).find(
            'h1', {'data-e2e': 'user-title'}).text.strip()
        self.page_data['followers'] = soupify(header_element).find(
            'strong', {'data-e2e': 'followers-count'}).text.strip()
        self.page_data['likes'] = soupify(header_element).find(
            'strong', {'data-e2e': 'likes-count'}).text.strip()
        self.page_data['establishement'] = f'/api/establishment/{self.establishment}'
        self.page_data['source'] = 'tiktok'

        try:
            self.page.click(
                "div.tiktok-x6f6za-DivContainer-StyledDivContainerV2.eq741c50")
            self.page.wait_for_timeout(10000)
            self.posts.append(extract_post())
            x = 0
            while self.page.locator("css=[data-e2e='arrow-right']").is_visible() and x < 20:
                self.page.click("css=[data-e2e='arrow-right']")
                self.page.wait_for_timeout(2000)
                self.posts.append(extract_post())
                x += 1
        except:
            pass

        self.page_data['posts'] = len(self.posts)

    # def save(self) -> None:
    #     print('==> Saving data')
    #     with open('./demo_tiktok.json', 'a') as openfile:
    #         openfile.write(json.dumps(self.data))
    #     self.data = {}

    def execute(self) -> None:
        # self.goto_login()
        # self.fill_loginform()
        # input("Press a key to continue ...")
        for item in self.items:
            print("Itérer ...")
            self.set_item(item)
            self.goto_tiktok_page()
            self.extract_data()
            self.save()

        self.stop()
