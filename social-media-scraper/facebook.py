from scraping import Scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from abc import abstractmethod
import sys
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from langdetect import detect
import re
import json
from models import create


class Facebook(Scraping):
    def __init__(self, url: str, establishment: str, site_url: str, post_file: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, site_url=site_url)
        self.post_file = post_file

    def login(self):
        self.scrap(self.site_url)
        time.sleep(10)
        login_form = self.driver.find_element(
            By.XPATH, "//form[@data-testid='royal_login_form']")
        email_input = login_form.find_element(
            By.XPATH, "//input[@data-testid='royal_email']").send_keys("0340851090")
        password_input = login_form.find_element(
            By.XPATH, "//input[@data-testid='royal_pass']").send_keys("p$Rlo6&3")
        time.sleep(5)
        login_form.find_element(
            By.XPATH, "//button[@data-testid='royal_login_button']").click()

    def get_posts_count(self):
        with open(self.post_file, 'r', encoding='utf-8') as file:
            items = json.load(file)
            return len(items.values())

    def load_posts(self, page_id):
        items = []

        with open(self.post_file, 'r', encoding='utf-8') as file:
            items = json.load(file)

        posts = []

        for item in items.values():
            try:
                posts.append({
                    "title": item["content"],
                    "comments": item["comments"],
                    "likes": item["reactions"]["likes"]+item["reactions"]["loves"]+item["reactions"]["wow"],
                    "share": item["shares"],
                    "publishedAt": datetime.strptime(item["posted_on"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d"),
                    "socialPage": f"/api/social_pages/{page_id}"
                })
            except Exception as e:
                print(e)
                pass

        return posts

    def format_posts(self):
        items = []

        results = ""

        with open(self.post_file, 'r', encoding='utf-8') as file:
            items = json.load(file)

        for item in items:
            try:
                d = {
                    "title": item["title"].replace('\n', ''),
                    "comments": item["comments"],
                    "likes": item["likes"],
                    "share": item["share"],
                    "publishedAt": datetime.strptime(item["publishedAt"], "%d/%m/%Y").strftime("%Y-%m-%d"),
                }
                results += json.dumps(d) + "#"
            except Exception as e:
                print(e)
                pass

        return results

    def extract(self) -> None:
        def format_number(number):
            nb = number.split()
            if len(nb) == 3:
                if ',' in nb[0] and nb[1] == 'K':
                    return nb[0].replace(',', '') + '00'
                elif nb[1] == 'K':
                    return nb[0] + '000'
            else:
                return nb[0]

        try:
            for i in range(5):
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)

            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            likes = soup.find_all('a', href=lambda href: href and "friends_likes" in href)[
                0].text.strip()
            followers = soup.find_all('a', href=lambda href: href and "followers" in href)[
                0].text.strip()
            nb_followers = int(format_number(followers))
            nb_likes = int(format_number(likes))

            nb_posts = self.get_posts_count()

            data = {
                "source": "facebook",
                "followers": nb_followers,
                "likes": nb_likes,
                "posts": nb_posts,
                "establishment": f"/api/establishments/{self.establishment}",
            }

            self.data = data

        except Exception as e:
            print('extraction file')
            print(e)

    def save(self):
        print("** Upload page")
        page = create(entity='social_pages', data=self.data)
        res = page.save()
        print(res)

        posts = self.load_posts(res['id'])

        for p in posts:
            post = create(entity='social_posts', data=p)
            print(post.save())


instance = Facebook(url="https://www.facebook.com/TheChelseaPinesInn",
                    post_file="datas/madamevacance.json", establishment=33, site_url="https://www.facebook.com")
# instance.execute()
print(instance.format_posts())
# instance.save()
