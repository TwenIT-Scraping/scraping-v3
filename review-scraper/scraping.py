# from seleniumwire import webdriver
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
import requests

TOR_PROXY = "socks5://127.0.0.1:9150"

def get_ip(use_tor:bool) -> None:
    print("getting IP")
    global TOR_PROXY
    session = requests.session()
    if(use_tor):
      session.proxies = {'http': TOR_PROXY, 'https': TOR_PROXY}
    try:
        response = session.get('http://httpbin.org/ip')
        print(f"Ip used befor tor connexion : {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

class Scraping(object):

    def __init__(self, 
                 in_background: bool, 
                 url: str, 
                 establishment: str, 
                 settings: str, 
                 env: str, 
                 last_review_date: str,
                 force_refresh=False) -> None:
        # driver options
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.70',
            'Mozilla/5.0 (Linux; Android 11; SM-G991U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.6 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Windows NT 7.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Version/11.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'Mozilla/5.0 (Linux; Android 10; Pixel 3 XL Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Mobile Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 OPR/79.0.4143.66'
            ]
        
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--disable-geolocation")
        # self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--disable-fingerprinting')
        # self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        # self.chrome_options.add_argument('--disable-gpu')
        # self.chrome_options.add_experimental_option('excludeSwitch',['enable-logging']) 
        self.chrome_options.add_argument("--enable-javascript")
        # self.chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
        self.chrome_options.add_argument('--log-level=3') 
        # in_background and self.chrome_options.add_argument('--headless')
        # self.chrome_options.add_argument('--incognito')

        self.firefox_options = webdriver.FirefoxOptions()
        self.firefox_options.add_argument('--disable-gpu')
        self.firefox_options.add_argument('--disable-blink-features=AutomationControlled')
        self.firefox_options.add_argument('--ignore-certificate-errors')
        in_background and self.firefox_options.add_argument('--headless')
        self.firefox_options.add_argument('--incognito')
        self.firefox_options.set_preference('intl.accept_languages', 'en-US, en')
        self.force_refresh = force_refresh

        dotenv.load_dotenv()
        # get_ip(False)
        # if os.environ.get('DRIVER') == 'chrome':
        #     global TOR_PROXY
        #     self.chrome_options.add_extension(f'{Path.cwd().joinpath("extensions/canvas_blocker_0_2_0_0.crx")}')
        #     self.chrome_options.add_extension(f'{Path.cwd().joinpath("extensions/browser_fingerprint_protector.crx")}')
        #     self.chrome_options.add_extension(
        #         f'{Path.cwd().joinpath("extensions/user_agent_1.crx")}')
        #     self.chrome_options.add_extension(
        #         f'{Path.cwd().joinpath("extensions/user_agent_2.crx")}')
            # self.chrome_options.add_argument(f"--proxy-server={TOR_PROXY}")
            # seleniumwireoptions = {
            #     "proxy": {
            #         "http": TOR_PROXY,
            #         "https": TOR_PROXY
            #     }
            # }
            # self.driver = webdriver.Chrome(options=self.chrome_options, seleniumwire_options=seleniumwireoptions)
        self.driver = webdriver.Chrome(options=self.chrome_options)
        # else:
        #     self.driver = webdriver.Firefox(options=self.firefox_options)
            # self.driver.install_addon(
            #     f'{Path.cwd().joinpath("extensions/canvasblocker-1.10.1.xpi")}')
        self.driver.maximize_window()
        # get_ip(True)
        self.data = {}
        self.url = url

        self.establishment = establishment
        self.settings = settings

        self.last_date = None
        self.env = env
        self.lang = 'fr'
        self.setting_id = "-1"
        self.last_review_date = last_review_date

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
        # self.set_random_params()

    def set_language(self, language: str) -> None:
        print("La langue du client: ", language.lower())
        self.lang = language.lower()

    def check_date(self, date, last_rev_date) -> bool:
        current_date = datetime.strptime(date, '%d/%m/%Y')
        last_revs_date = datetime.strptime(last_rev_date, '%d/%m/%Y')
        return current_date >= (current_date - timedelta(days=365)) or (current_date > (last_revs_date + timedelta(days=1)))
    #si cette condition est false, on ne prend plus les reviews, ça break

    def execute(self):
        print("executing scrap")
        try:

            if self.force_refresh:
                refresh_connection()
            print("here we go")
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
        # self.set_random_params()
        self.driver.get(self.url)
       # input('enter yes: ')

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

        result = []

        for item in self.data:
            if check_value(item):
                # line = '$$$$$'.join([item['author'], item['source'], item['language'], item['rating'], item['establishment'], item['date_review'],
                #                 item['comment'].replace('$', 'USD'), item['settings'], item['date_visit'], item['novisitday'], item['url'] if 'url' in item.keys() else 'non']) + "#####"
                # result += line
                item['comment'] = item['comment'].replace('$', 'USD')
                item['settings'] = item['settings'].split('/')[-1]
                item['establishment'] = item['establishment'].split('/')[-1]
                if 'url' in item.keys():
                    item['url'] = item['url']
                else:
                    item['url'] = ''
                result.append(item)

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
