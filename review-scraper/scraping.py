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
import dotenv
import os
from changeip import refresh_connection


class Scraping(object):

    def __init__(self, in_background: bool, url: str, establishment: str, settings: str, env: str, force_refresh=False) -> None:

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
        self.force_refresh = force_refresh

        dotenv.load_dotenv()

        if os.environ.get('SYSTEM') == 'linux':
            self.driver = webdriver.Chrome(options=self.chrome_options) if os.environ.get(
                'DRIVER') == 'chrome' else webdriver.Firefox(options=self.firefox_options)
        else:
            self.driver = webdriver.Chrome(service=ChromeService(
                ChromeDriverManager().install()), options=self.chrome_options) if os.environ.get('DRIVER') == 'chrome' else webdriver.Firefox(service=FirefoxService(
                    GeckoDriverManager().install()), options=self.firefox_options)

        self.driver.maximize_window()

        self.data = {}
        self.url = url

        self.establishment = establishment
        self.settings = settings

        self.last_date = None
        self.env = env

    def set_last_date(self, date):
        self.last_date = datetime.strptime(date, '%d/%m/%Y')

    def set_establishment(self, establishment):
        self.establishment = establishment

    def set_url(self, url: str) -> None:
        self.url = url

    def check_date(self, date) -> bool:
        current_date = datetime.strptime(date, '%d/%m/%Y')

        print("Date à vérifier: ", current_date.strftime('%d/%m/%Y'))

        # if self.last_date:
        #     print("A comparer avec: ", self.last_date)
        #     return current_date >= self.last_date
        # else:
        print("A comparer avec: ", datetime.now() + timedelta(days=-365))
        return current_date >= current_date + timedelta(days=-365)

    def execute(self):
        try:

            if self.force_refresh:
                refresh_connection()

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
                        'rating', 'establishment', 'date_review', 'settings']

        def check_value(item):
            for key in column_order:
                if not item[key] or item[key] == '':
                    print("erreur: ", key)
                    return False
            return True

        result = ""
        review_score = ReviewScore()

        for item in self.data:
            if check_value(item):
                score_data = review_score.compute_score(
                    item['comment'], item['language'], item['rating'], item['source'])
                # score_data = {'feeling': 'neutre', 'score': 0, 'confidence': 0}
                if score_data['feeling'] and score_data['score'] and score_data['confidence']:
                    line = '$'.join([item['author'], item['source'], item['language'], item['rating'], item['establishment'], item['date_review'],
                                    item['comment'].replace('$', 'USD'), score_data['feeling'], score_data['score'], score_data['confidence'], item['settings'], item['date_visit'], item['novisitday']]) + "#"

                    if len(line.split('$')) == 13:
                        result += line

        self.formated_data = result

    def save(self) -> None:

        self.format()

        if self.formated_data:
            print(self.formated_data)
            Review.save_multi(self.formated_data, self.env)
            print(len(self.data), "reviews uploaded!")
        else:
            print("No review uploaded!")

    @abstractmethod
    def extract(self) -> None:
        pass
