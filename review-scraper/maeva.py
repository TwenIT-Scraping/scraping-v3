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


class Maeva(Scraping):
    def __init__(self, url: str, establishment: str):
        super().__init__(in_background=False, url=url, establishment=establishment)

    def load_reviews(self) -> None:
        self.driver.find_element(By.ID, 'avis-tout-cta').click()
        results = int(''.join([x for x in self.driver.find_element(By.ID, 'avis-comp-content').find_element(By.CLASS_NAME, 'ml-1').text if x.isdigit()]))
        for i in range(results//3):
            self.driver.find_element(By.ID, 'avis-cards-content-container').click()
            for k in range(3):
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(2)

    def extract(self) -> None:

        self.load_reviews()

        reviews = []

        try:
            soup  = BeautifulSoup(self.driver.page_source, 'lxml')
            review_cards = soup.find('div', {'id':'avis-cards-content-container'}).find_all('div', {'typeof':'comment'})
            
            for review in review_cards:
                date = review.find('span', {'property':'dateCreated'})['content']
                data = {}
                data['author'] = review.find('div', class_='date-publication').find('strong').text.strip()
                data['date_review'] = '/'.join(date.split('-')[::-1])
                data['comment'] = review.find('p', class_='avis-comment').text.strip() if review.find('p', class_='avis-comment') else ''
                data['rating'] = review.find('span', class_='score-text').text if review.find('span', class_='score-text') else 0
                data['language'] = detect(data['comment'])
                data['source'] = urlparse(self.url).netloc.split('.')[1]
                data['establishment'] = f'/api/establishments/{self.establishment}'
                reviews.append(data)

        except Exception as e:
            print('extraction file')
            print(e)

        self.data = reviews


# trp = Maeva(url="https://www.maeva.com/fr-fr/residence-cannes-villa-francia---maeva-home_49993.html")
# trp.execute()