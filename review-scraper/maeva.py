from scraping import Scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from abc import abstractmethod
import sys
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from langdetect import detect
from lingua import Language, LanguageDetectorBuilder
import random
import pandas as pd


class Maeva(Scraping):
    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, settings=settings, env=env)
        self.data_loaded = False

    def detect(text:str) -> str:
        if text:
            lang_code = {
                'Language.ENGLISH':'en',
                'Language.GERMAN':'de',
                'Language.SPANISH':'es',
                'Language.FRENCH':'fr',
            }

            languages = [Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.SPANISH]
            detector = LanguageDetectorBuilder.from_languages(*languages).build()
            try:
                return lang_code[f"{detector.detect_language_of(text)}"]
            except:
                return ''
            
    def formate_date(self, raw_date:str):
        split_date = raw_date.split(' ')
        today = datetime.now()
        if split_date[1] == 'jour':
            return datetime.strftime(today + timedelta(days=-1), '%d/%m/%Y')
        elif split_date[1] == 'jours':
            return datetime.strftime(today + timedelta(days=-(int(split_date[0]))), '%d/%m/%Y')
        if split_date[1] == 'semaine':
            return datetime.strftime(today + timedelta(days=-7), '%d/%m/%Y')
        elif split_date[1] == 'semaines':
            return datetime.strftime(today + timedelta(days=-7*int(split_date[0])), '%d/%m/%Y')
        elif split_date[1] == 'mois':
                return datetime.strftime(today + timedelta(days=-31*int(split_date[0])), '%d/%m/%Y')
        elif split_date[1] == 'an':
            return datetime.strftime(today + timedelta(days=-365), '%d/%m/%Y')
        elif split_date[1] == 'ans':
            return datetime.strftime(today + timedelta(days=-(int(split_date[0])*365)), '%d/%m/%Y')

    def load_reviews(self) -> None:
        time.sleep(2)
        try:
            self.driver.find_element(By.ID, 'didomi-notice-agree-button').click()
            time.sleep(2)
        except:
            pass
        self.driver.execute_script("popin({selector:'#avis-comp'});")
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Les plus récents')]").click()
        self.driver.find_element(By.ID, 'avis-cards-content-container').click()
        time.sleep(1)
        index = 0
        while not self.data_loaded:
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            if index == 5:
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)
                self.extract()
                self.save_data()
                index = 0
                time.sleep(2)
            index += 1

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

        reviews = []

        try:
            soupe = BeautifulSoup(self.driver.page_source, 'lxml')
            container = soupe.find('div', {'id':'avis-cards-content-container'})
            cards = container.find_all('article', {'typeof':'comment'})
            for card in cards:
                rating = card.find('div', {'class':'avis-comp-section flex-ai-center mr-1'}).find('div')['aria-label'][0]
                date_name = card.find('div', {'class':'date-publication pt-1'})
                author = date_name.find('strong').text
                date_review = self.formate_date(date_name.find('span').text.lower().replace('il y a ', ''))
                comment = card.find('p', {'class':'avis-comment'}).text.strip()
                language = detect(comment)
                source = urlparse(self.driver.current_url).netloc.split('.')[1]

                if date_review != "" and date_review is not None:
                    if (author or comment or rating != "0") and datetime.strptime(date_review, '%d/%m/%Y') > datetime.now() - timedelta(days=365):

                        reviews.append({
                            'rating': rating,
                            'author': author,
                            'date_review': date_review,
                            'comment': comment,
                            'language': language,
                            'url': self.driver.current_url,
                            'source': source,
                            'date_visit': date_review,
                            'novisitday': "1",
                            'establishment': f'/api/establishments/{self.establishment}',
                            'settings': f'/api/settings/{self.settings}',   
                        })
                if datetime.strptime(date_review, '%d/%m/%Y') < datetime.now() - timedelta(days=365):
                    self.data_loaded = True
                    return
            self.data = reviews
            print(self.data)

        except Exception as e:
            print('extraction file')
            print(e)

        self.data = reviews

    def execute(self):
        try:

            if self.force_refresh:
                self.refresh_connection()
            self.scrap()
            time.sleep(5)
            WebDriverWait(self.driver, 10)
            if self.check_page():
                self.load_reviews()
                time.sleep(2)
                self.save()
            else:
                print("!!!!!!!! Cette page n'existe pas !!!!!!!!")
            self.driver.quit()
        except Exception as e:
            print(e)
            self.driver.quit()
            sys.exit("Arret")


# trp = Maeva(url="https://www.maeva.com/fr-fr/residence-cannes-villa-francia---maeva-home_49993.html",
#             establishment=3, settings=1, env='DEV')
# trp.execute()
