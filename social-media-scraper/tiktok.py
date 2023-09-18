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


class Tiktok(Scraping):
    def __init__(self, url: str, establishment: str):
        super().__init__(url=url, in_background=False, establishment=establishment)

    def execute(self):
        try:
            self.scrap(self.url)
            self.extract()
            # self.save()
            # self.driver.quit()
        except Exception as e:
            print(e)
            self.driver.quit()
            sys.exit("Arret")

    def extract(self) -> None:
        def format_number(number):
            if '.' in number and number[-1] == 'K':
                return number.replace('.', '')[:-2] + '00'
            elif number[-1] == 'K':
                return number[:-2] + '000'
            else:
                return number

        # self.load_reviews()

        # reviews = []

        try:
            time.sleep(10)
            soup  = BeautifulSoup(self.driver.page_source, 'lxml')
            followers = soup.find('strong', {'data-e2e': 'followers-count'}).text.strip()
            nb_followers = format_number(followers)
            
            print(nb_followers)
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


instance = Tiktok(url="https://www.tiktok.com/@montcorvo", establishment=2)
instance.execute()