import os
import random
import pandas as pd
from scraping import Scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from langdetect import detect
from selenium.webdriver.common.keys import Keys
from lingua import Language, LanguageDetectorBuilder
from changeip import refresh_connection


class BaseGoogleScrap(Scraping):
    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, settings=settings, env=env)
        self.url_lang_code = {
            'fr':'fr-FR',
            'en':'en-EN',
            'es':'es-ES',
        }

    def load_reviews(self) -> None:

        try:
            time.sleep(2)
            self.driver.find_element(By.XPATH, f"//button[@jsname='b3VHJd']").click()
        except:
            pass
        try:
            self.driver.execute_script("window.scrollTo(0, 500);")
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
        scrollHeight = 500
        currentHeight = 0
        while not self.data_loaded:
            self.driver.execute_script(f"window.scrollTo({currentHeight}, {scrollHeight});")
            time.sleep(0.2)
            if index == 10:
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)
                self.extract()
                self.save_data()
                index = 0
            index += 1
            currentHeight = scrollHeight
            scrollHeight += 200
    
    def format_url(self, language:str) -> str:
        try:
            hl_params_inde = self.url.index('&hl=') + 4
            new_url = self.url[:hl_params_inde] + self.url_lang_code[language] + self.url[hl_params_inde + 5:]
            print(new_url)
            return new_url
        except ValueError:
            print(f"{self.url}&hl={self.url_lang_code[language]}" )
            return f"{self.url}&hl={self.url_lang_code[language]}" 


    def execute(self) -> None:
        try:

            if self.force_refresh:
                refresh_connection()
            url = self.format_url(self.lang)
            self.set_url(url)
            self.scrap()
            try:
                time.sleep(3)
                accept_btn = self.driver.find_element(
                    By.XPATH, "//span[contains(text(), 'Tout accepter') or contains(text(), 'Accept all')], or contains(text(), 'Aceptar todo')")
                self.driver.execute_script("arguments[0].click();", accept_btn)
                time.sleep(random.randint(2, 5))
            except:
                pass
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

    def formate_date(self, raw_date:str) -> str:
        split_date = raw_date.split(' ')
        today = datetime.now()
        language = self.detect(raw_date)
        if 'mes' in raw_date:
            language = 'es'
        match language:
            case "fr":

                if split_date[1] == 'jour':
                    return datetime.strftime(today + timedelta(days=-1), '%d/%m/%Y')
                elif split_date[1] == 'jours':
                    return datetime.strftime(today + timedelta(days=-(int(split_date[3]))), '%d/%m/%Y')
                if split_date[1] == 'semaine':
                    return datetime.strftime(today + timedelta(days=-7), '%d/%m/%Y')
                elif split_date[1] == 'semaines':
                    return datetime.strftime(today + timedelta(days=-7*int(split_date[3])), '%d/%m/%Y')
                elif split_date[1] == 'mois':
                    if split_date[0] == 'un':
                        return datetime.strftime(today + timedelta(days=-31), '%d/%m/%Y')
                    else:
                        return datetime.strftime(today + timedelta(days=-31*int(split_date[3])), '%d/%m/%Y')
                elif split_date[1] == 'an':
                    return datetime.strftime(today + timedelta(days=-365), '%d/%m/%Y')
                elif split_date[1] == 'ans':
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
                
    def save_data(self) -> None:
        new_data = []
        df = pd.DataFrame(self.data)
        df.drop_duplicates(subset=['rating', 'author', 'date_review', 'comment',
                           'language', 'source', 'date_visit', 'novisitday'], inplace=True)
        for i in range(len(df)):
            new_data.append(df.iloc[i].to_dict())
        self.data = new_data
        print("=>  Actual datas: ", len(self.data))


class Google(BaseGoogleScrap):

    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(url=url, establishment=establishment, settings=settings, env=env)

        self.chrome_options.add_argument(f'--lang={self.lang}')
        self.chrome_options.add_argument('--disable-translate')
        self.data_loaded = False
        # self.driver = webdriver.Chrome(options=self.chrome_options)

        self.driver.maximize_window()

    def extract(self) -> list:
        print('extraction..')
        reviews = []

        try:
            self.driver.find_element(
                By.XPATH, "//div[@role='listbox' and @jsname='fMAOF']").click()
            time.sleep(random.uniform(.5, 2.5))
            self.driver.find_element(
                By.XPATH, "//div[@role='option' and @data-value='2' and @data-hveid='CAMQkAY']").click()
            time.sleep(random.uniform(.2, 2))
        except:
            pass

        page = self.driver.page_source

        soupe = BeautifulSoup(page, 'lxml')
        container = soupe.find('div', {'jsname':'SvNErb'})
        cards = container.find_all('div', {'class':'Svr5cf bKhjM'})

        for card in cards:
            author = card.find('a', {'class':'DHIhE QB2Jof'}).text.strip() if card.find('a', {'class':'DHIhE QB2Jof'}) else ""
            try:
                comment = card.find('div', {'class':'K7oBsc'}).find('span').text.replace('(Traducido por Google) ', '').replace('\xa0... Ver más', '').replace(" En savoir plus", "") \
                .replace('(Traduit par Google)', '').replace('(Traduce by Google)', '').lower() if card.find('div', {'class':'K7oBsc'}) else ""
                if "avis d'origine" in comment:
                    comment = comment.split("(avis d'origine)")[-1]
                if "(original)" in comment:
                    comment = comment.split("(original)")[-1]
            except:
                comment = ""
            rating = card.find('div', {'class': 'GDWaad'}).text.strip().split(
                '/')[0] if card.find('div', {'class': 'GDWaad'}) else "0"
            try:
                lang = detect(comment)
            except:
                lang = 'en'
            date_raw = card.find('span', {'class': 'iUtr1 CQYfx'}).text.lower()
            match(detect(date_raw)):
                case 'fr':
                    date_raw = date_raw.replace('il y a ', '').replace('\xa0','').strip() if card.find('span', {'class': 'iUtr1 CQYfx'}) else ""
                case 'es':
                    date_raw = date_raw.replace('hace ', '').replace('\xa0','').strip() if card.find('span', {'class': 'iUtr1 CQYfx'}) else ""
                case 'en':
                    date_raw = date_raw.replace('ago', '').replace('\xa0','').strip() if card.find('span', {'class': 'iUtr1 CQYfx'}) else ""
            date_review = self.formate_date(date_raw) if date_raw else ""

            if date_review != "" and date_review is not None:
                if (author or comment or rating != "0") and datetime.strptime(date_review, '%d/%m/%Y') > datetime.now() - timedelta(days=365):
                    reviews.append({
                        'rating': rating,
                        'author': author,
                        'date_review': date_review,
                        'comment': comment,
                        'language': lang,
                        'source': urlparse(self.driver.current_url).netloc.split('.')[1],
                        'date_visit': date_review,
                        'novisitday': "1"
                    })
                if datetime.strptime(date_review, '%d/%m/%Y') < datetime.now() - timedelta(days=365):
                    self.data_loaded = True
                    return
        self.data = reviews

# trp = Google(url="https://www.google.com/travel/hotels/entity/ChYIqtL21OvSv65QGgovbS8wdnB3cTRzEAE/reviews?utm_campaign=sharing&utm_medium=link&utm_source=htls&ts=CAEaIAoCGgASGhIUCgcI6A8QAxgLEgcI6A8QAxgMGAEyAhAAKgkKBToDTUdBGgA&ved=0CAAQ5JsGahcKEwiY1evEleyEAxUAAAAAHQAAAAAQAw",
#                 establishment=3, settings=1, env="DEV")
# trp.set_language('es')
# trp.execute()
# print(trp.data)
