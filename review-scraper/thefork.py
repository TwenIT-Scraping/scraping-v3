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
from langdetect import detect
from tools import month_number
from selenium.webdriver.support.select import Select
from iteration_utilities import unique_everseen
from changeip import refresh_connection


class Thefork(Scraping):
    def __init__(self, url: str, establishment: str, settings: str):
        refresh_connection()
        super().__init__(in_background=False, url=url,
                         establishment=establishment, settings=settings)

    def extract(self):
        def get_review_count() -> int:
            try:
                review_count_container = int(self.driver.find_element(
                    By.XPATH, "//div[@data-testid='restaurant-page-reviews-count']").text.strip())
                return review_count_container
            except:
                return 1

        def format_date(date: list) -> str:
            months = {
                'janvier': '01',
                'fevrier': '02',
                'mars': '03',
                'avril': '04',
                'mai': '05',
                'juin': '06',
                'juillet': '07',
                'aout': '08',
                'septembre': '09',
                'octobre': '10',
                'novembre': '11',
                'decembre': '12'
            }
            formated_date = f"{date[0]}/{months[date[1]]}/{date[2]}"
            return formated_date

        time.sleep(15)

        review_count = get_review_count()

        reviews = []

        while len(list(unique_everseen(reviews))) < review_count:
            try:
                self.driver.find_element(
                    By.CSS_SELECTOR, "#root > div.css-yg5c6u.ehxxr8o8 > div.css-20te3v.ehxxr8o4 > div.css-t5d95i.ehxxr8o1 > div:nth-child(10) > div > div.css-wxii5q.elkhwc30 > div.css-kabp9.elkhwc30 > button").click()
                WebDriverWait(self.driver, 20)
            except:
                pass

            try:
                self.driver.find_element(
                    By.CLASS_NAME, "styles_discloseChevron__kqPf_").click()
            except:
                pass

            page = self.driver.find_element(
                By.XPATH, "//div[@data-testid='review-list-wrapper']").get_attribute('innerHTML')

            soupe = BeautifulSoup(page, 'lxml')

            review_cards = soupe.find_all(
                'div', {'data-testid': 'restaurant-page-review-item'})

            for card in review_cards:
                comment = card.find('p', {'data-test': "read-more"}).text.strip(
                ) if card.find('p', {'data-test': "read-more"}) else ""
                date_review = format_date(
                    card.find('p', {'class': "css-1exvo68 ef3wbs40"}).text.strip().split(' '))
                rating = card.find('span', {'class': "css-ddyzjw e7dhrrp0"}).text.strip(
                ) if card.find('span', {'class': "css-ddyzjw e7dhrrp0"}) else ""
                author = card.find('cite', {'class': "css-1q25rhf ef3wbs40"}).text.strip(
                ) if card.find('cite', {'class': "css-1q25rhf ef3wbs40"}) else ""
                try:
                    lang = detect(comment)
                except:
                    lang = 'en'

                try:
                    reviews.append({
                        'comment': comment,
                        'rating': rating,
                        'date_review': date_review,
                        'language': lang,
                        'source': urlparse(self.url).netloc.split('.')[1],
                        'author': author,
                        'establishment': f'/api/establishments/{self.establishment}',
                        'settings': f'/api/settings/{self.settings}'
                    })
                except Exception as e:
                    print(e)
                    continue

        self.data = list(unique_everseen(reviews))


trp = Thefork(url="https://www.thefork.fr/restaurant/best-western-alexander-park-r308265",
              establishment=3, settings=1)
trp.execute()
print(trp.data)
