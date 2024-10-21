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
    def __init__(self, url: str, establishment: str, settings: str, env: str, last_review_date : str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, settings=settings, env=env, last_review_date=last_review_date)
        self.reviews_data = []

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

            print("reviews: ", len(reviews_list))

            for item in reviews_list:

                comment = item.find('span', {'data-test': 'wrapper-tag'}).text.strip(
                ) if item.find('span', {'data-test': 'wrapper-tag'}) else ""

                # print(comment)

                try:
                    rating_text = item.find('div', {'class': 'vJWFYZLiWZbHIB0Hwa83'})[
                        'aria-label']

                    # full_star = item.find_all(
                    #     'i', {'data-testid', 'star-full'})
                    # print("rate: ", len(full_star))
                    rating = f"{rating_text.split(' ')[0]}/5"
                    # print(rating)
                    # rating_container = item.find(
                    #     'div',).parent
                    # rating_items = rating_container.find_all('span')
                    # rating = str(int(sum(map(lambda x: int(x.text.strip()), [
                    #              rating_items[1], rating_items[3], rating_items[5], rating_items[7]]))/4)) + '/5'
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
                    'settings': f'/api/settings/{self.settings}',
                    'date_review': review_date,
                    'date_visit': review_date,
                    'novisitday': "1"
                })

            if len(self.reviews_data) and not self.check_date(self.reviews_data[-1]['date_review'], self.last_review_date):
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
                # print(e)
                break

        self.data = self.reviews_data


class Opentable_UK(Opentable):
    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(url=url, establishment=establishment, settings=settings, env=env)

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

                comment = item.find('span', {'data-testid': 'wrapper-tag'}).text.strip(
                ) if item.find('span', {'data-testid': 'wrapper-tag'}) else "" #attribut changé 
                author = item.find_all('section')[0].find_all('p')[0].text.strip()
                #Je pense qu'on ne prend pas les avis du site lui-même car tous ses avis sont au maximum
                """if 'opentable' in author.lower():
                    print("C'est un avis du site même, on zappe")
                    continue"""
                try:
                    """rating_container = item.find(
                        'span', string='overall').parent
                    rating_items = rating_container.find_all('span')
                    rating = str(int(sum(map(lambda x: int(x.text.strip()), [
                                 rating_items[1], rating_items[3], rating_items[5], rating_items[7]]))/4)) + '/5'"""
                    rating_container = item.find('ol',{'class' : 'gUG3MNkU6Hc- ciu9fF9m-z0-'})
                    #print('on a le container des <li> contenant les scores')
                    rating_items = rating_container.find_all('li')
                    #print('on a tous les <li>')
                    score = 0
                    for score_by_type in rating_items:
                        score = score + int(score_by_type.find('span').text.strip())
                    #print(f"on a tous les scores donnée par {author} et on va les divisé par 4 et le mettre sur 5")
                    rating = str(score / 4) + '/5'
                    print(f'Score = {rating}')
                    
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
                        'p', {'class': 'iLkEeQbexGs-'}).text.strip() #nouveau selecteur
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
                    'author': author,
                    'establishment': f'/api/establishments/{self.establishment}',
                    'settings': f'/api/settings/{self.settings}',
                    'date_review': review_date,
                    'date_visit': review_date,
                    'novisitday': "1"
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
