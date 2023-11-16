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


class Yelp(Scraping):
    def __init__(self, url: str, establishment: str, settings: str):
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

        def format_date(date: list):
            print(date)
            months = {
                'Jan': '01',
                'Feb': '02',
                'Mar': '03',
                'Apr': '04',
                'May': '05',
                'Jun': '06',
                'Jul': '07',
                'Aug': '08',
                'Sep': '09',
                'Oct': '10',
                'Nov': '11',
                'Dec': '12'
            }
            return f"{date[1]}/{months[date[0]]}/{date[2]}"

        time.sleep(15)

        pages = 1
        try:
            pages = int(self.driver.find_element(
                By.CLASS_NAME, 'css-1aq64zd').text[-1])
        except:
            pass

        reviews = []

        for i in range(pages):
            self.driver.find_element(
                By.XPATH, "//a[@aria-label='Next']").click()
            WebDriverWait(self.driver, 5)

            container = self.driver.find_element(
                By.ID, "reviews").get_attribute('innerHTML')
            soupe = BeautifulSoup(container, 'lxml')
            comments = soupe.find_all('li', {'class': "css-1q2nwpv"})

            for comment in comments:
                rating = 0
                try:
                    rating = int(comment.find(
                        'div', {'class': "css-14g69b3", 'role': 'img'})['aria-label'].split(' ')[0])
                except:
                    pass

                data = {
                    'author': comment.find('a', {'class': 'css-19v1rkv'}).text.strip(),
                    'date_review': format_date(comment.find('span', {'class': 'css-chan6m'}).text.replace(',', '').split(' ')),
                    'language': comment.find('span', {'class': "raw__09f24__T4Ezm"})['lang'],
                    'rating': rating,
                    'source': urlparse(self.url).netloc.split('.')[1],
                    'establishment': f'/api/establishments/{self.establishment}',
                    'settings': f'/api/settings/{self.settings}'
                }

                reviews.append(data)

        self.data = list(unique_everseen(reviews))


trp = Yelp(url="https://www.yelp.com/biz/28-50-wine-workshop-and-kitchen-london",
           establishment=3, settings=1)
trp.execute()
print(trp.data)
