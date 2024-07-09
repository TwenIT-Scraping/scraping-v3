from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from abc import abstractmethod
import sys
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from models import Review
import dotenv
import os
from changeip import refresh_connection
import random
import string
from pathlib import Path
from lingua import Language, LanguageDetectorBuilder


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

        if os.environ.get('DRIVER') == 'chrome':
            self.chrome_options.add_extension(
                f'{Path((str(Path.cwd()) + "/canvas_blocker_0_2_0_0.crx"))}')
            self.driver = webdriver.Chrome(options=self.chrome_options)
        else:
            self.driver = webdriver.Firefox(options=self.firefox_options)
            self.driver.install_addon(
                f'{Path((str(Path.cwd()) + "/canvasblocker-1.10.1.xpi"))}')

        self.driver.maximize_window()

        self.data = {}
        self.url = url

        self.establishment = establishment
        self.settings = settings

        self.last_date = None
        self.env = env
        self.lang = 'fr'
        self.setting_id = "-1"

        self.set_random_params()

    def set_random_params(self):
        random_params = ""
        length = random.randint(1, 5)
        param_characters = string.ascii_letters
        value_characters = string.ascii_letters + string.digits

        for i in range(length):
            key_length = random.randint(1, 6)
            value_length = random.randint(2, 20)
            random_params += '&'+''.join(random.choices(param_characters, k=key_length)) \
                + '='+''.join(random.choices(value_characters, k=value_length))

        self.url = self.url + '?' + \
            random_params[1:] if self.url.endswith(
                '.html') else self.url + random_params

    def detect(self, text: str) -> str:
        if text:
            lang_code = {
                'Language.ENGLISH': 'en',
                'Language.GERMAN': 'de',
                'Language.SPANISH': 'es',
                'Language.FRENCH': 'fr',
            }

        languages = [Language.ENGLISH, Language.FRENCH,
                     Language.GERMAN, Language.SPANISH]
        detector = LanguageDetectorBuilder.from_languages(*languages).build()
        try:
            return lang_code[f"{detector.detect_language_of(text)}"]
        except:
            return ''

    def set_setting_id(self, setting_id):
        self.setting_id = setting_id

    def set_last_date(self, date):
        self.last_date = datetime.strptime(date, '%d/%m/%Y')

    def set_establishment(self, establishment):
        self.establishment = establishment

    def set_url(self, url: str) -> None:
        self.url = url
        self.set_random_params()

    def set_language(self, language: str) -> None:
        print("La langue du client: ", language.lower())
        self.lang = language.lower()

    def check_date(self, date) -> bool:
        current_date = datetime.strptime(date, '%d/%m/%Y')
        return current_date >= (current_date - timedelta(days=365))

    def execute(self):
        try:

            if self.force_refresh:
                refresh_connection()

            self.scrap()
            time.sleep(5)
            WebDriverWait(self.driver, 10)
            if self.check_page():
                self.extract()
                time.sleep(2)
                self.save()
            else:
                print("!!!!!!!! Cette page n'existe pas !!!!!!!!")
            self.driver.quit()
        except Exception as e:
            print(e)
            self.driver.quit()
            sys.exit("Arret")

    def scrap(self) -> None:
        self.set_random_params()
        self.driver.get(self.url)

    def refresh(self) -> None:
        self.driver.refresh()

    def exit(self) -> None:
        self.driver.quit()
        sys.exit("Arret")

    def check_page(self) -> None:
        return True

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

        for item in self.data:
            print(item)
            if check_value(item):
                line = '$$$$$'.join([item['author'], item['source'], item['language'], item['rating'], item['establishment'], item['date_review'],
                                item['comment'].replace('$', 'USD'), item['settings'], item['date_visit'], item['novisitday'], item['url'] if 'url' in item.keys() else 'non']) + "#####"

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
