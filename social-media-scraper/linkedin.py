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
        actions.login(self.driver, 'joharyandrianjafimanohisolo@gmail.com', 'jOx3rBNT5Ax9')        

    def extract(self) -> None:
        try:
            soup  = BeautifulSoup(self.driver.page_source, 'lxml')
            infos = soup.find_all('div', {'class': 'org-top-card-summary-info-list__info-item'})
            followers = int(''.join([item.text.strip() for item in infos if 'abonnés' in item.text.strip()][0].split()[:-1]))
            print(followers)

            self.scrap(f"{self.url}/posts/?feedView=all")
            time.sleep(random.randint(5, 10))

            posts = soup.find_all('div', {'class': 'ember-view'})
            print(len(posts))
            # for post in posts:
            #     try:
            #         self.posts.append({
            #             'title': post.find('div', {'class': 'update-components-update-v2__commentary'}).text.strip(),
            #             'comments': post.find('li', {'class': 'social-details-social-counts__comments'}).text.strip(),
            #             'share': post.find('li', {'class': 'social-details-social-counts__item--with-social-proof'}).text.strip(),
            #             'likes': post.find('span', {'class': 'social-details-social-counts__reactions-count'}).text.strip(),
            #             'publishedAt': post.find('a', {'class': 'app-aware-link'})['aria-label']
            #         })
            #     except Exception as e:
            #         print(e)

            print(self.posts)

            # tab = followers.split(' ')
            # print(tab)
            # nb = tab[0].replace(',', ' ') + ('000' if len(tab) > 1 and tab[1] == 'K' else '')
            # print(nb)
            # review_cards = soup.find('div', {'id':'avis-cards-content-container'}).find_all('div', {'typeof':'comment'})
            
            # for review in review_cards:
            #     date = review.find('span', {'property':'dateCreated'})['content']
            #     data = {}
            #     data['author'] = review.find('div', class_='date-publication').find('strong').text.strip()
            #     data['date_review'] = '/'.join(date.split('-')[::-1])
            #     data['comment'] = review.find('p', class_='avis-comment').text.strip() if review.find('p', class_='avis-comment') else ''
            #     data['rating'] = review.find('span', class_='score-text').text if review.find('span', class_='score-text') else 0
            #     data['language'] = detect(data['comment'])
            #     data['source'] = urlparse(self.url).netloc.split('.')[1]
            #     data['establishment'] = f'/api/establishments/{self.establishment}'
            #     reviews.append(data)

        except Exception as e:
            print('extraction file')
            print(e)

        # self.data = reviews


instance = Linkedin(url="https://www.linkedin.com/company/dream-hotel-group/", establishment=2)
instance.execute()