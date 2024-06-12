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
from selenium.webdriver.common.keys import Keys
from lingua import Language, LanguageDetectorBuilder
from changeip import refresh_connection


class BaseGoogleScrap(Scraping):
    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, settings=settings, env=env)
        self.url_lang_code = {
            'fr': 'fr-FR',
            'en': 'en-EN',
            'es': 'es-ES',
        }
        self.data_loaded = False
        self.data = []

    def detect_lang(self, text: str) -> str:
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

    def is_handball(self) -> bool:
        return True if '&topic=mid:/' in self.driver.current_url else False
    
    def is_travel(self) -> bool:
        return True if '/travel/' in self.driver.current_url else False


    def load_reviews(self) -> None:
        if not self.is_travel():
            order_item = self.driver.find_elements(
                By.XPATH, "//div[@jsname='XPtOyb']")[1]
            self.driver.execute_script("arguments[0].click();", order_item)
            time.sleep(1)
        else:
            try:
                time.sleep(2)
                self.driver.find_element(
                    By.XPATH, f"//button[@jsname='b3VHJd']").click()
            except:
                pass
            try:
                self.driver.execute_script("window.scrollTo(0, 500);")
                order_dropdown = self.driver.find_element(
                    By.XPATH, "//div[@jsname='wQNmvb']")
                self.driver.execute_script(
                    "arguments[0].click();", order_dropdown)
                time.sleep(2)
                order_item = self.driver.find_elements(
                    By.XPATH, "//div[@jsname='V68bde']/div[@jsname='wQNmvb']")[1]
                self.driver.execute_script("arguments[0].click();", order_item)
                time.sleep(1)
            except:
                print("pass review order ...")
                pass

        index = 0
        scrollHeight = 500
        currentHeight = 0
        self.data_current_count = len(self.data)
        time.sleep(random.randint(1, 3))
        while not self.data_loaded:
            print(self.data_loaded)
            self.driver.execute_script(
                f"window.scrollTo({currentHeight}, {scrollHeight});")
            time.sleep(random.randint(1, 3))
            if index == 20:
                self.driver.find_element(
                    By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)
                self.extract()
                self.save_data()
                self.new_data_count = len(self.data)
                if self.new_data_count == self.data_current_count:
                    break
                self.data_current_count = self.new_data_count
                index = 0

            # else:
            #     for i in range(3):
            #         print('scrolling')
            #         self.driver.find_element(
            #             By.XPATH, '//div[@jsaction="WFrRFb;keydown:uYT2Vb"]').send_keys(Keys.PAGE_DOWN)
            #     if index == 10:
            #         self.extract()
            #         self.save_data()
            #         self.new_data_count = len(self.data)
            #         index = 0
            #         if self.new_data_count == self.data_current_count:
            #             print('breaked')
            #             break
            #         self.data_current_count = self.new_data_count

            index += 1
            currentHeight = scrollHeight
            scrollHeight += 200

    def format_url(self, language: str) -> str:
        try:
            hl_params_index = self.url.index('&hl=') + 4
            new_url = self.url[:hl_params_index] + \
                self.url_lang_code[language] + self.url[hl_params_index + 5:]
            print(new_url)
            return new_url
        except ValueError:
            print(f"{self.url}&hl={self.url_lang_code[language]}")
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
                self.save()
            else:
                print("!!!!!!!! Cette page n'existe pas !!!!!!!!")
            self.driver.quit()
        except Exception as e:
            print('error execution')
            print(e)
            self.driver.quit()
            sys.exit("Arret")

    def detect_date_lang(self, date:str) -> str:
        if date in ['jour', 'jours', 'semaine', 'semaines', 'mois', 'an', 'ans']:
            return 'fr'
        elif date in ['days', 'week', 'weeks', 'month', 'months', 'year', 'years']:
            return 'en'
        elif date in ['día', 'días', 'semana', 'semanas', 'mes', 'año', 'año']:
            return 'es'
        return ''


    def formate_date(self, raw_date: str) -> str:
        split_date = raw_date.split(' ')
        print(split_date)
        today = datetime.now()
        language = self.detect_date_lang(split_date[1])
        match language:
            case "fr":
                if split_date[1] == 'jour':
                    return datetime.strftime(today + timedelta(days=-1), '%d/%m/%Y')
                elif split_date[1] == 'jours':
                    return datetime.strftime(today + timedelta(days=-(int(split_date[0]))), '%d/%m/%Y')
                if split_date[1] == 'semaine':
                    return datetime.strftime(today + timedelta(days=-7), '%d/%m/%Y')
                elif split_date[1] == 'semaines':
                    return datetime.strftime(today + timedelta(days=-7*int(split_date[0])), '%d/%m/%Y')
                elif split_date[1] == 'mois':
                    if split_date[0] == 'un':
                        return datetime.strftime(today + timedelta(days=-31), '%d/%m/%Y')
                    else:
                        return datetime.strftime(today + timedelta(days=-31*int(split_date[0])), '%d/%m/%Y')
                elif split_date[1] == 'an':
                    return datetime.strftime(today + timedelta(days=-365), '%d/%m/%Y')
                elif split_date[1] == 'ans':
                    return datetime.strftime(today + timedelta(days=-(int(split_date[0])*365)), '%d/%m/%Y')
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

        try:
            soupe = BeautifulSoup(page, 'lxml')
            container = ''
            cards = []
            if self.is_handball():
                container = soupe.find('div', {'class': 'aSzfg'})
                cards = container.find_all('div', {'class': 'bwb7ce'})
                print(f"{len(cards)} handball cards found")
            elif self.is_travel():
                container = soupe.find('div', {'jsname':'SvNErb'})
                cards = container.find_all('div', {'class':'Svr5cf bKhjM'})
                print(f"{len(cards)} google travel cards found")
            else:
                container = soupe.find('div', {'jsname': 'SvNErb'})
                cards = container.find_all('div', {'class': 'Svr5cf bKhjM'})
                print(f"{len(cards)} simple google cards found")

            for card in cards:

                author = ''
                comment = ''
                date_raw = ''
                rating = 0
                date_review = ''
                date_visit = ''

                if self.is_travel():
                    author = card.find('a', {'class':'DHIhE QB2Jof'}).text.strip() if card.find('a', {'class':'DHIhE QB2Jof'}) else ""
                    try:
                        comment = card.find('div', {'class':'K7oBsc'}).find('span').text.replace('(Traducido por Google) ', '').replace('\xa0... Ver más', '').replace(" En savoir plus", "") \
                        .replace('(Traduit par Google)', '').replace('(Traduce by Google)', '').lower().split('(original)')[-1] if card.find('div', {'class':'K7oBsc'}) else ""
                        if comment and "avis d'origine" in comment:
                            comment = comment.split("(avis d'origine)")[-1]
                        if comment and "(original)" in comment:
                            comment = comment.split("(original)")[-1]
                    except:
                        comment = ""
                    url = ''
                    try:
                        url = card.find('a', {'class':'YhR3n'}, href=True)['href']
                    except:
                        url = self.driver.current_url

                    rating = card.find('div', {'class': 'GDWaad'}).text.strip() if card.find('div', {'class': 'GDWaad'}) else rating
                    date_raw = card.find('span', {'class': 'iUtr1 CQYfx'}).text.lower()

                    if 'sur' in date_raw:
                        date_raw = date_raw[:date_raw.index(' sur')]
                    if 'on' in date_raw:
                        date_raw = date_raw[:date_raw.index(' on')]
                    if 'en' in date_raw:
                        date_raw = date_raw[:date_raw.index(' en')]

                    date_raw = date_raw.replace('il y a ', '').replace('\xa0', ' ').replace('hace ', '').replace('ago', '')

                else:
                    author = card.find('div', {'class': 'Vpc5Fe'}).text.strip(
                    ) if card.find('div', {'class': 'Vpc5Fe'}) else ''
                    try:
                        comment = card.find('div', {'class': 'OA1nbd'}).text.strip().replace('(Traducido por Google) ', '').replace('\xa0... Ver más', '').replace(" En savoir plus", "") \
                            .replace('(Traduit par Google)', '').replace('(Traduce by Google)', '').lower() if card.find('div', {'class': 'OA1nbd'}) else ''
                        if comment and "avis d'origine" in comment:
                            comment = comment.split("(avis d'origine)")[-1]
                        if comment and "(original)" in comment:
                            comment = comment.split("(original)")[-1]
                    except:
                        print('Google handball comment exception')
                        pass
                    rating = '/'.join(card.find('div', {'class': 'dHX2k'})['aria-label'].replace('\xa0', '').replace(
                        'Note: ', '').replace(',', '.').split(' sur')) if card.find('div', {'class': 'dHX2k'}) else rating
                    date_raw = card.find(
                        'span', {'class': 'y3Ibjb'}).text.lower().replace('\xa0', ' ')
                    
                    date_raw = date_raw.replace('il y a ', '').replace('\xa0', '').replace('hace ', '').replace('ago', '')
                try:
                    lang = self.detect_lang(comment)
                except:
                    lang = 'en'
  
                date_review = self.formate_date(date_raw)
                if date_review != "" and date_review is not None:
                    if (author or comment or rating != "0") and datetime.strptime(date_review, '%d/%m/%Y') > datetime.now() - timedelta(days=365):
                        reviews.append({
                            'rating': rating,
                            'author': author,
                            'date_review': date_review,
                            'url': self.driver.current_url,
                            'comment': comment,
                            'language': lang,
                            'source': urlparse(self.driver.current_url).netloc.split('.')[1],
                            'date_visit': date_review,
                            'establishment': f'/api/establishments/{self.establishment}',
                            'settings': f'/api/settings/{self.settings}',
                            'novisitday': "1"
                        })

                    if datetime.strptime(date_review, '%d/%m/%Y') < (datetime.now() - timedelta(days=365)):
                        print("houla")
                        self.data = reviews
                        self.data_loaded = True
                        return
                    if self.data_loaded:
                        self.data = reviews
                        return
            print(reviews)
            self.data = reviews
        except Exception as e:
            print(e)
            

# trp = Google(url="https://www.google.com/search?sca_esv=cd9a55a255ee4ca7&biw=1920&bih=927&tbm=lcl&sxsrf=ADLYWILRiVyqj3TFZjsMeIPm77of3r5guQ:1715336316458&q=Sport+2000+Chamb%C3%A9ry+Avis&rflfq=1&num=20&stick=H4sIAAAAAAAAAONgkxIxNLA0NbY0NjazNDAztTAzMDKyNNvAyPiKUTK4IL-oRMHIwMBAwTkjMTfp8MqiSgXHssziRay45QB7lzUBUwAAAA&rldimm=10953933690658602296&hl=fr-FR&sa=X&ved=2ahUKEwiVhMDe7YKGAxXrVKQEHZyHCoYQ9fQKegQINxAF#lkt=LocalPoiReviews",
#                 establishment=3, settings=1, env="DEV")
# trp.set_language('fr')
# trp.execute()
# print(trp.data)
