from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
import time
from datetime import datetime
from bs4 import BeautifulSoup
import dotenv
import os
from api import ERApi
from changeip import refresh_connection


class Scraping(object):

    def __init__(self, in_background: bool, url: str, establishment: str, env: str, force_refresh=False) -> None:

        # driver options
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument(
            '--disable-blink-features=AutomationControlled')
        in_background and self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--incognito')
        self.chrome_options.add_extension(f'{Path((str(Path.cwd()) + "/review-scraper/canvas_blocker_0_2_0_0.crx"))}')


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
        self.source = ""

        self.env = env
        self.force_refresh = force_refresh

    def set_establishment(self, establishment):
        self.establishment = establishment

    def set_url(self, url: str) -> None:
        self.url = url

    def execute(self) -> None:
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

    def scrap(self) -> None:
        self.driver.get(self.url)

    def exit(self) -> None:
        self.driver.quit()

    def save(self) -> None:
        if self.data == 0:
            print("!!!!! Erreur scraping: ", self.url)
        else:
            data = {
                "source": self.source,
                "establishment": f"/api/establishments/{self.establishment}",
                "score": self.data,
                "scoreDate": datetime.now().strftime("%Y-%m-%d")
            }
            print(data)
            post_instance = ERApi(
                method="post", entity="scores", env=self.env, body=data, params={})
            post_instance.execute()

    def extract(self) -> None:
        time.sleep(2)

        if self.css_selector:
            page = self.driver.page_source
            soupe = BeautifulSoup(page, 'lxml')

            score = float(soupe.find(self.balise, {self.attr: self.css_selector}).text.strip(
            ).replace(',', '.')) if soupe.find(self.balise, {self.attr: self.css_selector}) else 0

            self.data = score / 2 if score > 5 else score

        if self.xpath_selector:
            score = float(self.driver.find_element(By.XPATH, self.xpath_selector).text) \
                if self.driver.find_element(By.XPATH, self.xpath_selector) else 0

            self.data = score / 2 if score > 5 else score
