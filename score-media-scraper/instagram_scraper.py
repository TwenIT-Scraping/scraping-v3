import json
import os
from playwright.sync_api import sync_playwright
from nested_lookup import nested_lookup
from datetime import datetime, timedelta
import time
from scraping import Scraping
import re
from progress.bar import ChargingBar, FillingCirclesBar
from random import randint


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
        time.sleep(10)
        self.page.goto(self.url, timeout=50000)
        self.page.wait_for_timeout(6000)

    def extract_data(self) -> None:
        followers = 0
        name = ""

        #On utilise le secteur pour le score
        # if not self.xhr_page: 
        #     self.add_logging("Erreur extraction: GraphQL no trouvé!")
        #     pass
        
        #print(self.xhr_page)
        try:
            time.sleep(randint(2,3))
            close_popup_connexion = self.page.locator('xpath=/html/body/div[6]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div[1]/div/div/svg')
            close_popup_connexion.click()
        except:
            pass
        try:
            #followers = nested_lookup(key='follower_count', document=self.xhr_page)[0]
            #followers = self.page.locator('span[class="x5n08af x1s688f"]').nth(2).get_attribute('title')
            followers = self.page.evaluate('document.getElementsByClassName("x5n08af x1s688f")[1].getAttribute("title")')
            specfic_space = "\u202f"
            if specfic_space in followers:
                followers = int(self.page.evaluate('document.getElementsByClassName("x5n08af x1s688f")[1].getAttribute("title")').replace(specfic_space,''))
            else:
                followers = int(followers)
            print(f"{followers} followers de type {type(followers)}")
            name = self.page.locator('h2').first.text_content()
            print(f'Name {name} de type {type(name)}')
        except Exception as e:
            print(f'erreur dans Extract data()-> {e}')
            self.add_error(e)

        # try:
        #     name = nested_lookup(
        #         key='full_name', document=self.xhr_page)[0]
        # except Exception as e:
        #     self.add_error(e)

        try:
            if name == "" or followers == 0:
                raise ("Error on extraction: name or followers informations")

            self.page_data = {
                'followers': followers,
                'likes': 0,
                'source': "instagram",
                'establishment': f"/api/establishments/{self.establishment}",
                'name': f"instagram_{name}",
                'posts': 0
            }

            print(self.page_data)

        except Exception as e:
            self.add_error(e)
            pass

    def execute(self) -> None:
        progress = ChargingBar('Preparing ', max=3)
        self.set_current_credential(0)
        """progress.next()
        print(" | Open login page")
        self.goto_login()
        progress.next()
        print(" | Fill login page")
        self.fill_loginform()
        progress.next()
        print(" | Logged in!")"""
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
                print(f'Data to save for actual link -> {self.page_data}')
                if not self.has_errors():
                    print(" | Saving")
                    output_files.append(self.save())
                    self.add_logging(f"=> Saved in local file !")
                    p_item.next()
                    print(" | Saved")
            
        self.stop()

        return output_files
