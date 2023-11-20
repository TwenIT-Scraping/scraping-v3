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
    def __init__(self, url: str, establishment: str, settings: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, settings=settings)

    def load_reviews(self) -> None:
        def get_last_review_date():
            page = self.driver.page_source
            soupe = BeautifulSoup(page, 'lxml')
            last_review_cards = soupe.find(
                'div', {'id': 'avis-cards-content-container'}).find_all('div', {'typeof': 'comment'})[-1]
            date = last_review_cards.find('span', {'property': 'dateCreated'})[
                'content']
            return '/'.join(date.split('-')[::-1])

        allbtn = self.driver.find_element(By.ID, 'avis-tout-cta')
        self.driver.execute_script("arguments[0].click();", allbtn)

        sort_btn = self.driver.find_element(
            By.XPATH, "//div[@class='avis-filter' and contains(text(), 'Les plus récents')]")

        self.driver.execute_script("arguments[0].click();", sort_btn)

        time.sleep(1)

        results = int(''.join([x for x in self.driver.find_element(
            By.ID, 'avis-comp-content').find_element(By.CLASS_NAME, 'ml-1').text if x.isdigit()]))
        for i in range(results//3):
            if not self.check_date(get_last_review_date()):
                break
            btn = self.driver.find_element(
                By.ID, 'avis-cards-content-container')
            self.driver.execute_async_script("arguments[0].click()", btn)

            for k in range(3):
                self.driver.find_element(
                    By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(2)

    def extract(self) -> None:

        self.load_reviews()

        reviews = []

        try:
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            review_cards = soup.find(
                'div', {'id': 'avis-cards-content-container'}).find_all('div', {'typeof': 'comment'})

            for review in review_cards:
                date = review.find('span', {'property': 'dateCreated'})[
                    'content']
                data = {}
                data['author'] = review.find(
                    'div', class_='date-publication').find('strong').text.strip()
                data['date_review'] = '/'.join(date.split('-')[::-1])
                data['comment'] = review.find(
                    'p', class_='avis-comment').text.strip() if review.find('p', class_='avis-comment') else ''
                data['rating'] = review.find(
                    'span', class_='score-text').text if review.find('span', class_='score-text') else 0
                data['language'] = detect(data['comment'])
                data['source'] = urlparse(self.url).netloc.split('.')[1]
                data['establishment'] = f'/api/establishments/{self.establishment}'
                data['settings'] = f'/api/settings/{self.settings}'
                data['date_visit'] = data['date_review']
                data['novisitday'] = "0"
                reviews.append(data)

        except Exception as e:
            print('extraction file')
            print(e)

        self.data = reviews


# trp = Maeva(url="https://www.maeva.com/fr-fr/residence-cannes-villa-francia---maeva-home_49993.html")
# trp.execute()
