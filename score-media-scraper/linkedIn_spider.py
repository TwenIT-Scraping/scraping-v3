import json
from playwright.sync_api import sync_playwright
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
import time
from scraping import Scraping
from progress.bar import ChargingBar, FillingCirclesBar
import re
import sys


class LinkedInProfileScraper(Scraping):

    def __init__(self, items: list = []) -> None:
        super().__init__(items)
        self.set_credentials('linkedin')

        self.hotel_page_urls = []
        self.xhr_calls = {}
        self.data_container = []
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False, args=['--start-maximized'])
        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()

    def stop(self):
        self.context.close()

    # def scoll_down_page(self) -> None:
    #     for i in range(15):
    #         self.page.evaluate(
    #             "window.scrollTo(0, document.body.scrollHeight)")
    #         self.page.wait_for_timeout(10000)
    #         time.sleep(3)

    def goto_login(self) -> None:
        self.page.goto("https://www.linkedin.com/login/fr")
        self.page.wait_for_timeout(10000)

    def fill_loginform(self) -> None:
        self.page.wait_for_selector("[id='username']")
        self.page.locator("[id='username']").click()
        time.sleep(.5)
        self.page.fill("[id='username']", self.current_credential['email'])
        time.sleep(.8)
        self.page.locator("[id='password']").click()
        time.sleep(.8)
        self.page.fill("[id='password']", self.current_credential['password'])
        time.sleep(1)
        self.page.locator("[type='submit']").click()
        self.page.wait_for_timeout(60000)
        try:
            captcha = self.page.locator(
                'div.body__banner-wrapper').locator('h1')
            if captcha:
                input("Press enter when you have finished captcha resolution ...")
        except:
            pass

    def goto_page(self, page) -> None:
        # self.page.goto(self.url+'/posts/?feedView=all')
        self.page.goto(self.url+page)
        self.page.wait_for_timeout(10000)
        # self.scoll_down_page()

    def extract_data(self) -> None:

        def convert_count(value):
            value = value.replace(',', '')
            if 'k' in value:
                tmp = value.split('k')
                millier = int(tmp[0])
                centaine = int(tmp[1]) if len(tmp) > 1 and tmp[1] != "" else 0

                return (millier*1000)+(centaine*100)
            else:
                return int(value)

        soupe = BeautifulSoup(self.page.content(), 'lxml')

        followers = soupe.find('section', {'class': 'artdeco-carousel'}).find('li', {'class': 'artdeco-carousel__item'}).find('span', {'class': 'update-components-actor__description'}).find('span', {'class': 'visually-hidden'}).text.strip() if \
            soupe.find('section', {'class': 'artdeco-carousel'}) and soupe.find('section', {'class': 'artdeco-carousel'}).find('li', {'class': 'artdeco-carousel__item'}) and soupe.find('section', {'class': 'artdeco-carousel'}).find('li', {'class': 'artdeco-carousel__item'}).find('span', {'class': 'update-components-actor__description'}) and \
            soupe.find('section', {'class': 'artdeco-carousel'}).find('li', {'class': 'artdeco-carousel__item'}).find('span', {'class': 'update-components-actor__description'}).find('span', {'class': 'visually-hidden'}) else ""

        # followers = soupe.find('section', {'class': "org-company-info-module__container artdeco-card full-width"}).find(
        #     'p', {'class': "t-14 t-normal text-align-center"}).text.strip().replace('\u202f', '').split('\xa0')[0]
        try:
            followers = convert_count(followers.split(' ')[0].lower())
        except Exception as e:
            self.add_error(e)

        if not self.has_errors():
            self.page_data = {
                'followers': followers,
                'likes': 0,
                'source': "linkedin",
                'establishment': f"/api/establishments/{self.establishment}",
                'name': f"linkedin",
                'posts': 0
            }
        else:
            pass

    def execute(self) -> None:
        progress = ChargingBar('Preparing ', max=2)
        self.goto_login()
        progress.next()
        print(" | Open login page")
        self.fill_loginform()
        progress.next()
        print(" | Logged in!")
        output_files = []
        for item in self.items:
            p_item = FillingCirclesBar(item['establishment_name'], max=4)
            try:
                self.set_item(item)
                self.add_logging(f"Open page: {item['establishment_name']}")
                p_item.next()
                print(" | Open page")
                self.goto_page('/')
                p_item.next()
                print(" | Extracting data")
                self.extract_data()
                self.add_logging(f"=> Data extracted !")
                p_item.next()
                if not self.has_errors():
                    print(" | Saving")
                    output_files.append(self.save())
                    p_item.next()
                    self.add_logging(f"=> Saved in local file !")
                    print(" | Saved !")

                self.reset_error()
            except Exception as e:
                self.add_error(e)
                pass

        self.stop()

        return output_files
