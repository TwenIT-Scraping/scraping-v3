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
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from langdetect import detect
from tools import month_number


class Tripadvisor(Scraping):
    def __init__(self, url: str, establishment: str):
        super().__init__(in_background=False, url=url, establishment=establishment)

    def extract(self):
        reviews = []

        try:
            while True:
                page = self.driver.page_source

                soupe = BeautifulSoup(page, 'lxml')

                reviews_card = soupe.find_all('div', {'data-test-target':"HR_CC_CARD"})

                for item in reviews_card:

                    title = item.find('div', {'data-test-target':'review-title'}).text.strip() if item.find('div', {'data-test-target':'review-title'}) else ''
                    detail = item.find('span', {'class':'QewHA'}).find('span').text.strip().replace('\n', '') if item.find('span', {'class':'QewHA'}) else ''
                    comment = f"{title}{': ' if title and detail else ''}{detail}"
                    
                    try:
                        lang = detect(comment)
                    except:
                        lang = 'en'

                    year = datetime.today().year
                    month = datetime.today().month
                    day = datetime.today().day

                    try:
                        date_raw = re.search(r"\(.*\)", item.find('div', {'class': 'cRVSd'}).text.strip()).group()
                        if date_raw == '(Hier)' or '(Yesterday)':
                            last_day = datetime.today() + timedelta(days=-1)
                            year = str(last_day.month)
                            month = str(last_day.year)
                            day = str(last_day.day)
                        else:
                            date_rawt = date_raw[1:-1].split()
                            if date_rawt[0].isnumeric():
                                day = date_rawt[0]
                                month_number(date_rawt[1], 'fr', 'short')
                            else:
                                year = date_rawt[1]
                                month = month_number(date_rawt[0], 'fr', 'short')
                    except:
                        date_raw = item.find('div', {'class': 'cRVSd'}).text.strip()
                        year = date_raw.split()[-1]
                        month = month_number(date_raw.split()[-2], 'en', 'short')

                    review_data = {
                        'comment': comment,
                        'rating': str(int(item.find('span', class_='ui_bubble_rating')['class'][1].split('_')[1]) / 10) + "/5" if item.find('span', class_='ui_bubble_rating') else "0/5",
                        'language': lang,
                        'source': urlparse(self.url).netloc.split('.')[1],
                        'author': item.find('a', class_='ui_header_link').text.strip() if item.find('a', class_='ui_header_link') else "",
                        'establishment': f'/api/establishments/{self.establishment}',
                        'date_review': f"{day}/{month}/{year}"
                    }

                    reviews.append(review_data)

                try:
                    next_btn = self.driver.find_element(By.CSS_SELECTOR, "a.nav.next")
                    disable_btn = 'disabled' in next_btn.get_attribute('class').split()
                    if next_btn and not disable_btn:
                        self.driver.execute_script("arguments[0].click();", next_btn)
                        time.sleep(5)
                    else:
                        break
                    
                except Exception as e:
                    break

            self.data = reviews

        except Exception as e:
            print("erreur:", e)
        



# trp = Tripadvisor(url="https://www.tripadvisor.fr/Hotel_Review-g1056032-d1055274-Reviews-Madame_Vacances_Les_Chalets_de_Berger-La_Feclaz_Savoie_Auvergne_Rhone_Alpes.html")
# trp.execute()
# print(trp.data)