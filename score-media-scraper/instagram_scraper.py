import json
import os
from playwright.sync_api import sync_playwright
from nested_lookup import nested_lookup
from datetime import datetime, timedelta
import time
from scraping import Scraping
import re
from progress.bar import ChargingBar, FillingCirclesBar


class InstagramProfileScraper(Scraping):

    def __init__(self, items: list = []) -> None:
        super().__init__(items)
        self.set_credentials('instagram')

        self.xhr_page = None

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False, args=['--start-maximized'])
        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()
        self.source = "instagram"

    def clean_data(self):
        self.xhr_page = None
        self.page_data = {}

    def stop(self):
        self.context.close()

    def resolve_loginform(self) -> None:
        self.fill_loginform()

    def goto_login(self) -> None:
        self.page.goto(
            "https://www.instagram.com/accounts/login/", timeout=30000)
        self.page.wait_for_timeout(30000)

    def fill_loginform(self) -> None:
        self.page.wait_for_selector("[name='username']", timeout=30000)
        self.page.locator("[name='username']").click()
        time.sleep(.5)
        self.page.fill("[name='username']", self.current_credential['email'])
        time.sleep(.3)
        self.page.locator("[name='password']").click()
        time.sleep(.2)
        self.page.fill("[name='password']",
                       self.current_credential['password'])
        time.sleep(.1)
        self.page.locator("[type='submit']").click()
        self.page.wait_for_timeout(70000)

    def intercept_response(self, response) -> None:
        """capture all background requests and save them"""
        response_type = response.request.resource_type

        if response_type == "xhr":
            if 'graphql' in response.url:
                res = response.json()
                if 'data' in res.keys() and 'user' in res['data'].keys():
                    self.xhr_page = res['data']['user']

    def goto_insta_page(self) -> None:
        self.page.on("response", self.intercept_response)
        self.page.goto(self.url, timeout=50000)
        self.page.wait_for_timeout(6000)

    def extract_data(self) -> None:
        followers = 0
        name = ""

        if not self.xhr_page:
            self.add_logging("Erreur extraction: GraphQL no trouvé!")
            pass

        else:

            try:
                followers = nested_lookup(
                    key='follower_count', document=self.xhr_page)[0]
            except Exception as e:
                self.add_error(e)

            try:
                name = nested_lookup(
                    key='full_name', document=self.xhr_page)[0]
            except Exception as e:
                self.add_error(e)

            try:
                if name == "" or followers == 0:
                    raise ("Error on extraction: name or followers informations")

                self.page_data = {
                    'followers': followers,
                    'likes': 0,
                    'source': "instagram",
                    'establishment': f"/api/establishments/{self.establishment}",
                    'name': f"instagram_score_{name}",
                    'posts': 0
                }

                print(self.page_data)

            except Exception as e:
                self.add_error(e)
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
        output_files = []
        for item in self.items:
            p_item = FillingCirclesBar(item['establishment_name'], max=3)
            self.set_item(item)
            self.add_logging(f"Open page: {item['establishment_name']}")
            self.clean_data()
            p_item.next()
            print(" | Open page")
            self.goto_insta_page()
            p_item.next()
            print(" | Extracting")
            self.extract_data()
            self.add_logging(f"=> Data extracted !")
            p_item.next()
            if not self.has_errors():
                print(" | Saving")
                output_files.append(self.save())
                self.add_logging(f"=> Saved in local file !")
                p_item.next()
                print(" | Saved")

        self.stop()

        return output_files
