import os
import random

import pandas as pd
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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
# from googletrans import Translator
from lingua import Language, LanguageDetectorBuilder
from changeip import refresh_connection


class Google(Scraping):
    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, settings=settings, env=env)

    @abstractmethod
    def load_reviews(self):
        pass

    def execute(self):
        try:

            if self.force_refresh:
                refresh_connection()

            self.scrap()
            time.sleep(5)
            WebDriverWait(self.driver, 10)
            if self.check_page():
                self.load_reviews()
                time.sleep(2)
                # self.save()
            else:
                print("!!!!!!!! Cette page n'existe pas !!!!!!!!")
            self.driver.quit()
        except Exception as e:
            print(e)
            self.driver.quit()
            sys.exit("Arret")

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

    def formate_date(self, raw_date):
        split_date = raw_date.split(' ')
        today = datetime.now()
        language = self.detect(raw_date)
        if 'mes' in raw_date:
            language = 'es'
        match language:
            case "fr":

                if split_date[4] == 'jour':
                    return datetime.strftime(today + timedelta(days=-1), '%d/%m/%Y')
                elif split_date[4] == 'jours':
                    return datetime.strftime(today + timedelta(days=-(int(split_date[3]))), '%d/%m/%Y')
                if split_date[4] == 'semaine':
                    return datetime.strftime(today + timedelta(days=-7), '%d/%m/%Y')
                elif split_date[4] == 'semaines':
                    return datetime.strftime(today + timedelta(days=-7*int(split_date[3])), '%d/%m/%Y')
                elif split_date[4] == 'mois':
                    if split_date[3] == 'un':
                        return datetime.strftime(today + timedelta(days=-31), '%d/%m/%Y')
                    else:
                        return datetime.strftime(today + timedelta(days=-31*int(split_date[3])), '%d/%m/%Y')
                elif split_date[4] == 'an':
                    return datetime.strftime(today + timedelta(days=-365), '%d/%m/%Y')
                elif split_date[4] == 'ans':
                    return datetime.strftime(today + timedelta(days=-(int(split_date[3])*365)), '%d/%m/%Y')
                else:
                    return datetime.strftime(today, '%d/%m/%Y')

            case"en":
                if split_date[1] == 'days':
                    return datetime.strftime(today + timedelta(days=-(int(split_date[0]))), '%d/%m/%Y')
                if split_date[1] == 'week':
                    return datetime.strftime(today + timedelta(days=-7), '%d/%m/%Y')
                elif split_date[1] == 'weeks':
                    return datetime.strftime(today + timedelta(days=-7*int(split_date[0])), '%d/%m/%Y')
                elif split_date[1] == 'months' or split_date[1] == 'month':
                    if split_date[0] == 'a':
                        return datetime.strftime(today + timedelta(days=-31), '%d/%m/%Y')
                    else:
                        return datetime.strftime(today + timedelta(days=-31*int(split_date[0])), '%d/%m/%Y')
                elif split_date[1] == 'year':
                    return datetime.strftime(today + timedelta(days=-365), '%d/%m/%Y')
                elif split_date[1] == 'years':
                    return datetime.strftime(today + timedelta(days=-(int(split_date[0])*365)), '%d/%m/%Y')
                else:
                    return datetime.strftime(today, '%d/%m/%Y')
            case "es":
                if split_date[1] == 'día':
                    return datetime.strftime(today + timedelta(days=-1), '%d/%m/%Y')
                if split_date[1] == 'días':
                    return datetime.strftime(today + timedelta(days=-(int(split_date[0]))), '%d/%m/%Y')
                if split_date[1] == 'semana':
                    return datetime.strftime(today + timedelta(days=-7), '%d/%m/%Y')
                elif split_date[1] == 'semanas':
                    return datetime.strftime(today + timedelta(days=-7*int(split_date[0])), '%d/%m/%Y')
                elif split_date[1] == 'mes' or split_date[1] == 'meses':
                    if split_date[0] == 'un':
                        return datetime.strftime(today + timedelta(days=-31), '%d/%m/%Y')
                    else:
                        return datetime.strftime(today + timedelta(days=-31*int(split_date[0])), '%d/%m/%Y')
                elif split_date[1] == 'año':
                    return datetime.strftime(today + timedelta(days=-365), '%d/%m/%Y')
                elif split_date[1] == 'años':
                    return datetime.strftime(today + timedelta(days=-(int(split_date[0])*365)), '%d/%m/%Y')
                else:
                    return datetime.strftime(today, '%d/%m/%Y')


class Google_ES(Google):
    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(url=url,
                         establishment=establishment, settings=settings, env=env)

        self.chrome_options.add_argument(f'--lang=es')
        self.chrome_options.add_argument('--disable-translate')
        self.data_loaded = False
        self.driver = webdriver.Chrome(options=self.chrome_options)


        # if os.environ.get('SYSTEM') == 'linux':
        #     self.driver = webdriver.Chrome(options=self.chrome_options) if os.environ.get(
        #         'DRIVER') == 'chrome' else webdriver.Firefox(options=self.firefox_options)
        # else:
        #     self.driver = webdriver.Chrome(service=ChromeService(
        #         ChromeDriverManager().install()), options=self.chrome_options) if os.environ.get('DRIVER') == 'chrome' else webdriver.Firefox(service=FirefoxService(
        #             GeckoDriverManager().install()), options=self.firefox_options)

        self.driver.maximize_window()

    def load_reviews(self):
        # def get_last_review_date():
        #     page = self.driver.page_source
        #     soupe = BeautifulSoup(page, 'lxml')
        #     last_review_cards = soupe.find_all('div', {'jsname': "Pa5DKe"})[-1]
        #     date_raw = last_review_cards.find('span', {'class': 'iUtr1'}).text.strip(
        #     ) if last_review_cards.find('span', {'class': 'iUtr1'}) else ""
        #     comment = last_review_cards.find('div', {'class': 'K7oBsc'}).find('span').text.strip()\
        #         .replace(" En savoir plus", "") if last_review_cards.find('div', {'class': 'K7oBsc'}) else ""
        #     try:
        #         lang = detect(comment)
        #     except:
        #         lang = 'en'
        #     return self.formate_date(date_raw, lang) if date_raw else "01/01/1999"
        # try:
        #     self.driver.find_element(
        #         By.XPATH, "//div[@aria-label='Avis' and @aria-controls='reviews' and @role='tab']").click()
        #     time.sleep(2)
        # except:
        #     pass

        try:
            self.driver.find_element(By.CSS_SELECTOR, 'span.VfPpkd-vQzf8d').click()
            time.sleep(2)
        except:
            pass
        try:
            self.driver.execute_script(f"window.scrollTo(0, 500);")
            order_dropdown = self.driver.find_element(By.XPATH, "//div[@jsname='wQNmvb']")
            self.driver.execute_script("arguments[0].click();", order_dropdown)
            time.sleep(2)
            order_item = self.driver.find_elements(By.XPATH, "//div[@jsname='V68bde']/div[@jsname='wQNmvb']")[1]
            self.driver.execute_script("arguments[0].click();", order_item)
            time.sleep(1)
        except Exception as e:
            print("pass review order ...")
            print(e)
        pass

        index = 0
        while not self.data_loaded:
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            if index == 10:
                for k in range(2):
                    self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)
                time.sleep(1)
                self.extract()
                self.save_data()
                index = 0
            index += 1

        # index = 0

        # try:
        #     accept_btn = self.driver.find_element(
        #         By.XPATH, "//span[contains(text(), 'Tout accepter') or contains(text(), 'Accept all')]")
        #     self.driver.execute_script("arguments[0].click();", accept_btn)
        #     time.sleep(random.randint(2, 5))
        # except:
        #     print("pass accept all button ...")
        #     pass

        # time.sleep(5)

        # try:
        #     self.driver.find_element(
        #         By.XPATH, "//div[@aria-label='Avis' and @aria-controls='reviews' and @role='tab']").click()
        #     time.sleep(2)
        # except:
        #     print("pass reviews tab click")
        #     pass

        # try:
        #     self.driver.execute_script(
        #         f"window.scrollTo(0, 500);")
        #     index += 1
        #     order_dropdown = self.driver.find_element(
        #         By.XPATH, "//div[@jsname='wQNmvb']")
        #     self.driver.execute_script("arguments[0].click();", order_dropdown)
        #     time.sleep(2)
        #     order_item = self.driver.find_elements(
        #         By.XPATH, "//div[@jsname='V68bde']/div[@jsname='wQNmvb']")[1]
        #     self.driver.execute_script("arguments[0].click();", order_item)
        #     time.sleep(1)
        # except Exception as e:
        #     print("pass review order ...")
        #     print(e)
        #     pass

        # new_frame_height = frame_height = self.driver.execute_script(
        #     "return document.querySelector('div[jsname=\"KYYiw\"]').scrollHeight")

        # while True:
        #     new_frame_height = self.driver.execute_script(
        #         "return document.querySelector('div[jsname=\"KYYiw\"]').scrollHeight")
        #     height = (frame_height/20)*index

        #     # Scroll down to bottom
        #     try:
        #         self.driver.execute_script(
        #             f"window.scrollTo(0, {str(height)});")
        #         index += 1

        #         # Wait to load page
        #         time.sleep(1)
        #         new_datas = self.extract()
        #         self.save_data(new_datas)
        #     except Exception as e:
        #         print(e)

        #     if height == new_frame_height:
        #         break

        #     if datetime.strptime(self.my_datas[-1]['date_review'], '%d/%m/%Y') < datetime.now() - timedelta(days=31):
        #         break

    def save_data(self) -> None:
        new_data = []
        df = pd.DataFrame(self.data)
        df.drop_duplicates(subset=['rating', 'author', 'date_review', 'comment',
                           'language', 'source', 'date_visit', 'novisitday'], inplace=True)
        for i in range(len(df)):
            new_data.append(df.iloc[i].to_dict())
        self.data = new_data
        print("=>  Actual datas: ", len(self.data))

    def extract(self) -> None:

        try:
            page = self.driver.page_source

            soupe = BeautifulSoup(page, 'lxml')

            review_container = soupe.find_all('div', {'jsname': 'SvNErb'})

            for container in review_container:
                cards = container.find_all('div', {'class': 'Svr5cf bKhjM'})
                for card in cards:
                    author = card.find('a', {'class': 'DHIhE QB2Jof'}).text.strip(
                    ) if card.find('a', {'class': 'DHIhE QB2Jof'}) else ""
                    # print(author)
                    try:
                        comment = card.find('div', {'class': 'K7oBsc'}).find('span').text.replace('(Traducido por Google) ', '').replace('\xa0... Ver más', '').replace(" En savoir plus", "") \
                            .replace('(Traduit par Google)', '').replace('(Traduce by Google)', '').lower().split('(original)')[-1] if card.find('div', {'class': 'K7oBsc'}) else ""
                    except:
                        comment = ""
                    # print(comment)
                    rating = card.find('div', {'class': 'GDWaad'}).text.strip().split(
                        '/')[0] if card.find('div', {'class': 'GDWaad'}) else "0"
                    # print(rating)
                    try:
                        lang = self.detect(comment)
                    except:
                        print("Exception langue!!!")
                        lang = 'en'
                    # print(lang)
                    date_raw = card.find(
                        'span', {'class': 'iUtr1 CQYfx'}).text.lower()
                    # print(date_raw)
                    match(self.detect(date_raw)):
                        case 'es':
                            date_raw = date_raw.replace('hace ', '').replace(
                                '\xa0', '').strip() if card.find('span', {'class': 'iUtr1 CQYfx'}) else ""
                        case _:
                            date_raw = date_raw.lower().replace('\xa0', '').strip(
                            ) if card.find('span', {'class': 'iUtr1 CQYfx'}) else ""

                    # print(date_raw)
                    date_review = self.formate_date(
                        date_raw) if date_raw else ""
                    print(date_review)

                    if date_review != "":
                        if (author != "" or comment != "" or rating != "0") and datetime.strptime(date_review, '%d/%m/%Y') > datetime.now() - timedelta(days=365):
                            d = {
                                'rating': rating,
                                'author': author,
                                'date_review': date_review,
                                'comment': comment,
                                'language': lang,
                                'source': urlparse(self.url).netloc.split('.')[1],
                                'establishment': f'/api/establishments/{self.establishment}',
                                'settings': f'/api/settings/{self.settings}',
                                'date_visit': date_review,
                                'novisitday': "1"
                            }
                            self.data.append(d)
                    
                        if datetime.strptime(date_review, '%d/%m/%Y') < datetime.now() - timedelta(days=365):
                            self.data_loaded = True
                            return
                    

        except Exception as e:
            print("Exception: ", e)


trp = Google_ES(url="https://www.google.com/travel/hotels/entity/ChYIqtL21OvSv65QGgovbS8wdnB3cTRzEAE/reviews?utm_campaign=sharing&utm_medium=link&utm_source=htls",
                establishment=3, settings=1, env="DEV")
trp.set_language('es')
trp.execute()
print(trp.my_datas)
