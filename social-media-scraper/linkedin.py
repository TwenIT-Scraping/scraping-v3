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
from linkedin_scraper import actions
import random


class Linkedin(Scraping):
    def __init__(self, url: str, establishment: str):
        super().__init__(in_background=False, url=url, establishment=establishment)
        self.posts = []

    def execute(self):
        self.login()
        time.sleep(random.randint(2, 10))
        self.scrap(self.url)
        time.sleep(random.randint(5, 10))
        self.extract()

    def login(self):
        time.sleep(5)
        actions.login(self.driver, 'joharyandrianjafimanohisolo@gmail.com', 'jOx3rBNT5Ax9')
        time.sleep(5)       

    def extract(self) -> None:
        try:
            time.sleep(10)
            soup  = BeautifulSoup(self.driver.page_source, 'lxml')
            infos = soup.find_all('div', {'class': 'org-top-card-summary-info-list__info-item'})
            followers = int(''.join([item.text.strip() for item in infos if 'abonnés' in item.text.strip()][0].split()[:-1]))
            print(followers)

            self.scrap(f"{self.url}/posts/?feedView=all")
            time.sleep(random.randint(15, 30))

            # post_container = soup.find('div', class_='scaffold-finite-scroll__content')
            # post_ = post_container.find_all('div', class_='occludable-update')
            # posts = []

            # for post in post_:
            #     comments = post.find('li', {'class': "social-details-social-counts__item social-details-social-counts__comments social-details-social-counts__item--with-social-proof"}).text.strip().split(' ')[0] if \
            #         post.find('li', {'class': "social-details-social-counts__item social-details-social-counts__comments social-details-social-counts__item--with-social-proof"}) else 0
            #     shares =  post.find('li', {'class':"social-details-social-counts__item social-details-social-counts__item--with-social-proof"}).text.strip().split(' ')[:-15] if \
            #         post.find('li', {'class':"social-details-social-counts__item social-details-social-counts__item--with-social-proof"}) else 0
            #     title = post.find('span', {'class':"break-words"}).text.strip() if post.find('span', {'class':"break-words"}) else ""  
            #     likes = int(post.find('span', {'class': "social-details-social-counts__reactions-count"}).text.strip()) if \
            #         post.find('span', {'class': "social-details-social-counts__reactions-count"}) else 0
            #     posts.append({
            #         "title": title,
            #         "likes": likes,
            #         "comments": comments,
            #         "shares": shares
            #     })

            # print(posts)

        except Exception as e:
            print('extraction file')
            print(e)


instance = Linkedin(url="https://www.linkedin.com/company/dream-hotel-group/", establishment=1)
instance.execute()