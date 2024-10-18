import re
from playwright.sync_api import sync_playwright
from nested_lookup import nested_lookup
from random import randint
from datetime import datetime
import time
import json
from bs4 import BeautifulSoup
from scraping import Scraping
from dateutil.relativedelta import relativedelta
from progress.bar import ChargingBar, FillingCirclesBar


class TikTokProfileScraper(Scraping):

    def __init__(self, items: list = []) -> None:
        super().__init__(items)

        self.hotel_page_urls = []
        self.data = {}

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False, args=['--start-maximized'], channel='chrome')
        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()

    def stop(self):
        self.context.close()

    def resolve_loginform(self) -> None:
        pass

    def check_captcha(self) -> None:
        pass

    def goto_login(self) -> None:
        self.page.goto(
            "https://www.tiktok.com/login/phone-or-email/email", timeout=40000)

    def fill_loginform(self) -> None:
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
        self.page.goto(self.url, timeout=1000000)
        self.page.wait_for_timeout(25000)
        time.sleep(10)

    def extract_data(self) -> None:

        def soupify(element: str) -> object:
            return BeautifulSoup(element, 'lxml')

        def extract_post() -> dict | None:
            self.page.wait_for_selector(
                "div.css-1xlna7p-DivProfileWrapper.ekjxngi4")
            try:
                next_post = self.page.locator(
                    "div.css-1xlna7p-DivProfileWrapper.ekjxngi4").inner_html()
                element = soupify(next_post)

                date_list = element.find(
                    'span', {'data-e2e': "browser-nickname"}).find_all('span')[-1].text.split('-')

                if len(date_list) == 3:
                    publishedAt = f"{'0' + date_list[0] if len(date_list[0]) == 1 else date_list[0]}-{'0' + date_list[1] if len(date_list[1]) == 1 else date_list[1]}-{date_list[2]}"
                elif len(date_list) == 2:
                    publishedAt = f"{datetime.now().year}-{'0' + date_list[0] if len(date_list[0]) == 1 else date_list[0]}-{'0' + date_list[1] if len(date_list[1]) == 1 else date_list[1]}"
                else:
                    day = int(''.join(filter(str.isdigit, date_list[0])))
                    publishedAt = (datetime.now(
                    ) - relativedelta(days=day)).strftime("%Y-%m-%d")

                data = {
                    'title': element.find('div', {'data-e2e': "browse-video-desc"}).text.strip(),
                    'publishedAt': publishedAt,
                    'likes': element.find('strong', {'data-e2e': "browse-like-count"}).text.strip(),
                    'comments': element.find('strong', {'data-e2e': "browse-comment-count"}).text.strip(),
                    'share': element.find('strong', {'data-e2e': "undefined-count"}).text.strip()
                }
            except Exception as e:
                print(e)

            return data

        header_element = self.page.locator(
            "#app").inner_html()
        name = re.sub(r'[^\w]', ' ', soupify(header_element).find(
            'h1', {'data-e2e': 'user-title'}).text.strip())
        self.page_data['name'] = f"tiktok_{name}"
        #des int()
        self.page_data['followers'] = int(soupify(header_element).find(
            'strong', {'data-e2e': 'followers-count'}).text.strip())
        
        self.page_data['likes'] = int(soupify(header_element).find(
            'strong', {'data-e2e': 'likes-count'}).text.strip())
        
        self.page_data['establishment'] = f'api/establishments/{self.establishment}'
        self.page_data['source'] = 'tiktok'
        self.source = self.page_data['source']
        """
        try:
            self.page.locator(
                "css=[data-e2e='user-post-item'] a").first.click()
            self.page.wait_for_timeout(10000)
            self.posts.append(extract_post())
            x = 0
            while self.page.locator("css=[data-e2e='arrow-right']").is_visible() and x < 20:
                self.page.click("css=[data-e2e='arrow-right']")
                self.page.wait_for_timeout(10000)
                self.posts.append(extract_post())
                x += 1
        except Exception as e:
            print(e)
            pass

        #self.page_data['posts'] = len(self.posts)"""

    def execute(self):
        output_file = []
        for item in self.items:
            try:
                p_item = FillingCirclesBar(item['establishment_name'], max=4)
                self.set_item(item)
                p_item.next()
                print(" | Open page")
                self.goto_tiktok_page()
                p_item.next()
                print(" | Extracting")
                self.extract_data()
                p_item.next()
                print(" | Saving")
                output_file.append(self.save())
                p_item.next()
                print(" | Saved !")
                return output_file
            except Exception as e:
                print(e)

        self.stop()
