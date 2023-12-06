import random
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


class Google(Scraping):
    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, settings=settings, env=env)

    def formate_date(self, raw_date, lang="fr"):
        split_date = raw_date.split()
        print(raw_date)
        today = datetime.now()

        if lang == "fr":

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

        if lang == "en":
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

    def load_reviews(self):
        def get_last_review_date():
            page = self.driver.page_source
            soupe = BeautifulSoup(page, 'lxml')
            last_review_cards = soupe.find_all('div', {'jsname': "Pa5DKe"})[-1]
            date_raw = last_review_cards.find('span', {'class': 'iUtr1'}).text.strip(
            ) if last_review_cards.find('span', {'class': 'iUtr1'}) else ""
            comment = last_review_cards.find('div', {'class': 'K7oBsc'}).text.strip().replace(
                " En savoir plus", "") if last_review_cards.find('div', {'class': 'K7oBsc'}) else ""
            try:
                lang = detect(comment)
            except:
                lang = 'en'

            return self.formate_date(
                date_raw, lang) if date_raw else "01/01/1999"

        try:
            self.driver.find_element(
                By.XPATH, "//div[@aria-label='Avis' and @aria-controls='reviews' and @role='tab']").click()
            time.sleep(2)
        except:
            pass

        results = int(''.join([x for x in self.driver.find_element(
            By.CSS_SELECTOR, '#reviews > c-wiz > c-wiz > div > div > div > div > div.ChBWlb.TjtFVc > div.pDLIp > div > div.zhMoVd.nNUNpc > div.UkIqCb > div > span').text if x.isdigit()]))

        for i in range(results//6):
            if not self.check_date(get_last_review_date()):
                break

            time.sleep(1)
            self.driver.find_element(
                By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)

    def extract(self):

        time.sleep(3)

        try:

            try:
                accept_btn = self.driver.find_element(
                    By.XPATH, "//span[contains(text(), 'Tout accepter') or contains(text(), 'Accept all')]")
                self.driver.execute_script("arguments[0].click();", accept_btn)
                time.sleep(random.randint(2, 5))
            except:
                pass

            time.sleep(5)

            try:
                self.driver.find_element(
                    By.XPATH, "//div[@role='listbox' and @aria-label='Menu déroulant pour filtrer les avis']").click()
                time.sleep(random.uniform(.5, 2.5))
                self.driver.find_element(
                    By.XPATH, "//div[@role='option' and @data-value='2' and @aria-label='Plus récents']").click()
                time.sleep(random.uniform(.2, 2))
            except:
                pass

            self.load_reviews()

            reviews = []

            page = self.driver.page_source

            soupe = BeautifulSoup(page, 'lxml')

            review_container = soupe.find_all('div', {'jsname': "Pa5DKe"})

            for container in review_container:
                cards = container.find_all('div', {'data-hveid': True})
                for card in cards:
                    author = card.find('span', {'class': 'k5TI0'}).find('a').text.strip() if card.find(
                        'span', {'class': 'k5TI0'}) and card.find('span', {'class': 'k5TI0'}).find('a') else ""
                    comment = card.find('div', {'class': 'K7oBsc'}).text.strip().replace(
                        " En savoir plus", "") if card.find('div', {'class': 'K7oBsc'}) else ""
                    rating = card.find('div', {'class': 'GDWaad'}).text.strip().split(
                        '/')[0] if card.find('div', {'class': 'GDWaad'}) else "0"

                    try:
                        lang = detect(comment)
                    except:
                        lang = 'en'

                    date_raw = card.find('span', {'class': 'iUtr1'}).text.strip(
                    ) if card.find('span', {'class': 'iUtr1'}) else ""

                    date_review = self.formate_date(
                        date_raw, lang) if date_raw else "01/01/1999"

                    print(date_review)

                    if (author or comment or rating != "0") and date_review != '01/01/1999':

                        reviews.append({
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
                        })

            self.data = reviews
        except:
            pass


# trp = Google(url="https://www.google.com/travel/hotels/entity/ChYIqtL21OvSv65QGgovbS8wdnB3cTRzEAE/reviews?utm_campaign=sharing&utm_medium=link&utm_source=htls&ts=CAESABogCgIaABIaEhQKBwjnDxAKGAISBwjnDxAKGAMYATICEAAqCQoFOgNNR0EaAA", establishment=3)
# trp.execute()
# print(trp.data)
