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
# from models import Review
# from tools import ReviewScore


class Scraping(object):

    def __init__(self, in_background: bool, url: str = '', establishment: str = '3', site_url:str="") -> None:

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

        self.driver = webdriver.Firefox(service=FirefoxService(
                    GeckoDriverManager().install()), options=self.firefox_options)

        # self.driver = webdriver.Chrome(executable_path="C:/Programs/chromedriver/chromedriver.exe", options=self.chrome_options)

        self.driver.maximize_window()

        self.data = {}
        self.url = url

        self.establishment = establishment
        self.site_url = site_url

    def set_establishment(self, establishment):
        self.establishment = establishment

    def set_url(self, url: str) -> None:
        self.url = url

    def execute(self) -> None:
        try:
            self.login()
            time.sleep(5)
            self.scrap(self.url)
            self.extract()
            # time.sleep(2)
            # self.save()
            # self.driver.quit()
        except Exception as e:
            print(e)
            self.driver.quit()
            sys.exit("Arret")

    def scrap(self, url) -> None:
        self.driver.get(url)

    def refresh(self) -> None:
        self.driver.refresh()

    def exit(self) -> None:
        self.driver.quit()
        sys.exit("Arret")

    def login(self) -> None:
        pass

    # def format(self) -> None:
    #     result = ""
    #     review_score = ReviewScore()

    #     for item in self.data:
    #         score_data = review_score.compute_score(item['comment'], item['language'])
    #         result += '$'.join([item['author'], item['source'], item['language'], item['rating'], item['establishment'], item['date_review'], item['comment'], score_data['feeling'], score_data['score'], score_data['confidence']]) + "#"

    #     self.formated_data = result

    def save(self) -> None:

        pass
        
        # self.format()
        # Review.save_multi(self.formated_data)
        # print(len(self.data), "reviews uploaded!")


    @abstractmethod
    def extract(self) -> None:
        pass
