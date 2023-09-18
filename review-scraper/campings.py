from scraping import Scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.command import Command
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from abc import abstractmethod
import sys
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs


class Campings(Scraping):
    def __init__(self, url: str, establishment: str):
        super().__init__(in_background=False, url=url, establishment=establishment)

    def extract(self):

        review_toggle_btn = self.driver.find_element(By.ID, "toggle-reviews")
        self.driver.execute_script("arguments[0].click();", review_toggle_btn)
        time.sleep(.5)

        reviews = []

        while True:

            page = self.driver.page_source

            soupe = BeautifulSoup(page, 'lxml')

            review_cards = soupe.find('div', {'class': 'reviews__list'}).find_all('div', {'data-toggle': True})

            for card in review_cards:
                t = {
                    'comment': card.find('div', {'class': 'review__comment'}).text.strip() if card.find('div', {'class': 'review__comment'}) else "",
                    'rating': card.find('span', {'class': 'review__rating'}).text.strip().split('/')[0] if card.find('span', {'class': 'review__rating'}) else "0",
                    'date_review': card.find('div', {'class': 'review__publish-date'}).find('span').text.strip() if card.find('div', {'class': 'review__publish-date'}) else "01/01/2020",
                    'language': 'fr',
                    'source': urlparse(self.url).netloc.split('.')[1],
                    'author': card.find('div', {'class': 'review__author'}).text.strip() if card.find('div', {'class': 'review__author'}) else "",
                    'establishment': '/api/establishments/3'
                }
                
                t['author'] and reviews.append(t)

            try:
                next_btn = self.driver.find_element(By.CLASS_NAME, 'dca-pagination__next')
                hidden_btn = 'dca-pagination--hidden' in next_btn.get_attribute('class').split()

                if next_btn and not hidden_btn:
                    self.driver.execute_script("arguments[0].click();", next_btn)
                    time.sleep(4)
                else:
                    break
                
            except Exception as e:
                break

        self.data = reviews


# trp = Campings(url="https://www.campings.com/fr/camping/le-pearl-camping-paradis-76750#reviews")
# trp.execute()
# print(trp.data)