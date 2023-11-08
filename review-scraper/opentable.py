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
from random import randint
from dateutil import parser


class Opentable(Scraping):
    def __init__(self, url: str, establishment: str):
        super().__init__(in_background=False, url=url, establishment=establishment)
        self.reviews_data = []


class Opentable_UK(Opentable):
    def __init__(self, url: str, establishment: str):
        super().__init__(url=url, establishment=establishment)

    def extract(self):

        print(self.driver.current_url)

        while True:
            page = self.driver.page_source

            time.sleep(randint(1, 3))

            soupe = BeautifulSoup(page, 'lxml')

            if soupe.find('h3', string='Reviews could not be updated'):
                print("Refresh page")
                self.driver.refresh()
                time.sleep(5)
                self.extract()

            reviews_list = soupe.find_all(
                'li', {'data-test': 'reviews-list-item'})

            for item in reviews_list:

                comment = item.find('span', {'data-test': 'wrapper-tag'}).text.strip(
                ) if item.find('span', {'data-test': 'wrapper-tag'}) else ""

                try:
                    rating_container = item.find(
                        'span', string='overall').parent
                    rating_items = rating_container.find_all('span')
                    rating = str(int(sum(map(lambda x: int(x.text.strip()), [
                                 rating_items[1], rating_items[3], rating_items[5], rating_items[7]]))/4)) + '/5'
                except Exception as e:
                    rating = "0/5"
                    print(e)

                try:
                    lang = detect(comment)
                except:
                    lang = 'en'

                review_date = '01/01/1999'

                try:
                    date_raw = item.find(
                        'p', {'class': 'Xfrgl6cRPxn4vwFrFgk1'}).text.strip()
                    if date_raw[:8] == 'Dined on':
                        date = date_raw[9:]

                        review_date = datetime.strftime(
                            parser.parse(date), '%d/%m/%Y')
                    elif date_raw[-8:] == 'days ago':
                        review_date = datetime.strftime(
                            datetime.now() + timedelta(days=-int(date_raw.split()[1])), '%d/%m/%Y')
                except Exception as e:
                    review_date = '01/01/1999'

                review_date != '01/01/1999' and self.reviews_data.append({
                    'comment': comment,
                    'language': lang,
                    'rating': rating,
                    'source': urlparse(self.url).netloc.split('.')[1],
                    'author': item.find_all('section')[0].find_all('p')[0].text.strip(),
                    'establishment': f'/api/establishments/{self.establishment}',
                    'date_review': review_date
                })

            if not self.check_date(self.reviews_data[-1]['date_review']):
                break

            try:
                next_btn_div = self.driver.find_element(
                    By.XPATH, "//div[@data-test='pagination-next']")

                if next_btn_div:
                    next_btn = next_btn_div.find_element(By.XPATH, "./..")

                    if next_btn.find_element(By.XPATH, "./..").is_displayed():
                        self.driver.execute_script(
                            "arguments[0].click();", next_btn)
                        time.sleep(5)
                    else:
                        print("Dernière page !!!")
                        break
                else:
                    print("Bouton non trouvé !!!")
                    break

            except Exception as e:
                print(e)
                break

        self.data = self.reviews_data


# trp = OpenTable()
# trp.set_url("https://www.opentable.com/the-belvedere")
# trp.execute()
# print(trp.data)
