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


class Scraping(object):

    def __init__(self, in_background: bool, url: str, establishment: str, env: str) -> None:

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

        self.balise = ""
        self.attr = ""
        self.css_selector = ""

        self.xpath_selector = ""

        self.establishment = establishment

        self.env = env

    def set_establishment(self, establishment):
        self.establishment = establishment

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

    def scrap(self) -> None:
        self.driver.get(self.url)

    def exit(self) -> None:
        self.driver.quit()

    def save(self) -> None:
        print("Saving done!")

        # self.format()

        # if self.formated_data:
        #     print(self.formated_data)
        #     # Review.save_multi(self.formated_data, self.env)
        #     print(len(self.data), "reviews uploaded!")
        # else:
        #     print("No review uploaded!")

    def extract(self) -> None:
        time.sleep(2)

        page = self.driver.page_source

        soupe = BeautifulSoup(page, 'lxml')

        if self.css_selector:

            score = float(soupe.find(self.balise, {self.attr: self.css_selector}).text.strip(
            ).replace(',', '.')) if soupe.find(self.balise, {self.attr: self.css_selector}) else 0

            self.data = score / 2 if score > 5 else score

        if self.xpath_selector:
            print(self.driver.find_element(By.XPATH, self.xpath_selector).text)
            score = float(self.driver.find_element(By.XPATH, self.xpath_selector).text) \
                if self.driver.find_element(By.XPATH, self.xpath_selector) else 0

            self.data = score / 2 if score > 5 else score
