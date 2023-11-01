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
from models import Review
from tools import ReviewScore


class Scraping(object):

    def __init__(self, in_background: bool, url: str, establishment: str = '3') -> None:

        # driver options
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument(
            '--disable-blink-features=AutomationControlled')
        in_background and self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--incognito')

        self.firefox_options = webdriver.FirefoxOptions()
        self.firefox_options.add_argument('--disable-gpu')
        self.firefox_options.add_argument('--ignore-certificate-errors')
        in_background and self.firefox_options.add_argument('--headless')
        self.firefox_options.add_argument('--incognito')
        self.firefox_options.set_preference(
            'intl.accept_languages', 'en-US, en')

        self.driver = webdriver.Firefox(service=FirefoxService(
            GeckoDriverManager().install()), options=self.firefox_options)

        # self.driver = webdriver.Chrome(service=ChromeService(
        #     ChromeDriverManager().install()), options=self.chrome_options)

        self.driver.maximize_window()
        self.current_driver = 'firefox'

        self.min_cycle = 30
        self.max_cycle = 30
        self.driver_cycle = 30
        self.counter = 0

        self.data = {}
        self.url = url

        self.establishment = establishment

    def permute_driver(self) -> None:
        self.driver.quit()
        if self.current_driver == 'firefox':
            try:
                self.driver = webdriver.Chrome(options=self.chrome_options)
            except:
                self.driver = webdriver.Chrome(service=ChromeService(
                    ChromeDriverManager().install()), options=self.chrome_options)
            self.current_driver = 'chrome'
        else:
            try:
                self.driver = webdriver.Firefox(options=self.firefox_options)
            except:
                self.driver = webdriver.Firefox(service=FirefoxService(
                    GeckoDriverManager().install()), options=self.firefox_options)
            self.current_driver = 'firefox'
        self.counter = 0
        self.set_driver_cycle(randint(self.min_cycle, self.max_cycle))

    def set_driver_interval(self, min: int, max: int) -> None:
        self.min_cycle = min
        self.max_cycle = max
        self.set_driver_cycle(randint(self.min_cycle, self.max_cycle))

    def set_establishment(self, establishment):
        self.establishment = establishment

    def increment_counter(self) -> None:
        self.counter = self.counter + 1
        self.check_counter()

    def check_counter(self) -> None:
        if self.counter == self.driver_cycle:
            print("Changement de driver!!!")
            self.permute_driver()

    def set_driver_cycle(self, cycle: int) -> None:
        self.driver_cycle = cycle

    def set_url(self, url: str) -> None:
        self.url = url

    def execute(self) -> None:
        try:
            self.scrap()
            time.sleep(5)
            WebDriverWait(self.driver, 10)
            self.extract()
            time.sleep(2)
            self.save()
            self.driver.quit()
        except Exception as e:
            print(e)
            self.driver.quit()
            sys.exit("Arret")

    def scrap(self) -> None:
        self.driver.get(self.url)

    def refresh(self) -> None:
        self.driver.refresh()

    def exit(self) -> None:
        self.driver.quit()
        sys.exit("Arret")

    def format(self) -> None:
        column_order = ['author', 'source', 'language',
                        'rating', 'establishment', 'date_review', 'comment']

        def check_value(item):
            for key in column_order:
                if not item[key] or item[key] == '':
                    return False
            return True

        result = ""
        review_score = ReviewScore()

        for item in self.data:
            if check_value(item):
                score_data = review_score.compute_score(
                    item['comment'], item['language'], item['rating'], item['source'])
                if score_data['feeling'] and score_data['score'] and score_data['confidence']:
                    line = '$'.join([item['author'], item['source'], item['language'], item['rating'], item['establishment'], item['date_review'],
                                    item['comment'].replace('$', 'USD'), score_data['feeling'], score_data['score'], score_data['confidence']]) + "#"
                    if len(line.split('$')) == 10:
                        result += line

        self.formated_data = result

    def save(self) -> None:

        self.format()

        # with open('datta.txt', 'w', encoding='utf-8') as file:
        #     file.write(self.formated_data)

        Review.save_multi(self.formated_data)
        print(len(self.data), "reviews uploaded!")

    @abstractmethod
    def extract(self) -> None:
        pass
