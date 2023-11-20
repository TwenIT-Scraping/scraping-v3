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
    def __init__(self, url: str, establishment: str, settings: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, settings=settings)

    def extract(self):
        pass


class Tripadvisor_UK(Tripadvisor):
    def __init__(self, url: str, establishment: str, settings: str):
        super().__init__(url=url, establishment=establishment, settings=settings)

    def extract(self):
        reviews = []

        time.sleep(10)

        try:
            while True:
                page = self.driver.page_source

                soupe = BeautifulSoup(page, 'lxml')

                try:

                    reviews_card = soupe.find_all(
                        'div', {'data-test-target': "HR_CC_CARD"})

                    if len(reviews_card):

                        for item in reviews_card:
                            try:
                                title = item.find('div', {'data-test-target': 'review-title'}).text.strip(
                                ) if item.find('div', {'data-test-target': 'review-title'}) else ''
                            except:
                                print("Erreur titre")

                            try:
                                detail = item.find('span', {'class': 'QewHA'}).find('span').text.strip(
                                ).replace('\n', '') if item.find('span', {'class': 'QewHA'}) else ''
                            except:
                                print("Erreur detail")

                            try:
                                comment = f"{title}{': ' if title and detail else ''}{detail}"
                            except:
                                print("Erreur comment")

                            try:
                                lang = detect(comment)
                            except:
                                lang = 'en'

                            year = datetime.today().year
                            month = datetime.today().month
                            day = datetime.today().day

                            try:
                                date_raw = item.find(
                                    'div', {'class': 'cRVSd'}).text.strip()

                                print(date_raw)

                                date_rawt = date_raw.split()[-2:]

                                if int(date_rawt[1]) > 2000:
                                    year = date_rawt[1]
                                    day = (datetime.today() +
                                           timedelta(days=-1)).day
                                else:
                                    day = date_rawt[1]
                                    year = datetime.today().year

                                month = month_number(
                                    date_rawt[0], 'en', 'short')
                            except Exception as e:
                                print("Erreur date")
                                print(e)

                            review_data = {
                                'comment': comment,
                                'rating': str(int(item.find('span', class_='ui_bubble_rating')['class'][1].split('_')[1]) / 10) + "/5" if item.find('span', class_='ui_bubble_rating') else "0/5",
                                'language': lang,
                                'source': urlparse(self.url).netloc.split('.')[1],
                                'author': item.find('a', class_='ui_header_link').text.strip() if item.find('a', class_='ui_header_link') else "",
                                'establishment': f'/api/establishments/{self.establishment}',
                                'settings': f'/api/settings/{self.settings}',
                                'date_review': f"{day}/{month}/{year}"
                            }

                            reviews.append(review_data)
                    else:
                        raise Exception()

                except:
                    reviews_card = soupe.find_all(
                        'div', {'class': "review-container"})

                    for item in reviews_card:
                        title = item.find('a', {'class': 'title'}).text.strip()
                        detail = item.find(
                            'div', {'data-prwidget-name': 'reviews_text_summary_hsx'}).text.strip()

                        try:
                            comment = f"{title}{': ' if title and detail else ''}{detail}"
                        except:
                            print("Erreur comment")

                        try:
                            lang = detect(comment)
                        except:
                            lang = 'en'

                        rating_bubble = item.find(
                            'span', {'class': 'ui_bubble_rating'})['class'][1]
                        print(rating_bubble)
                        rating = str(
                            int(int(rating_bubble.split('_')[1])/10)) + '/5'

                        try:
                            date_raw = item.find(
                                'span', {'class': 'ratingDate'})['title']
                            print(date_raw)

                            date_rawt = date_raw.split()

                            month = month_number(date_rawt[1], 'fr', '')
                        except Exception as e:
                            print("Erreur date")
                            print(e)

                        review_data = {
                            'comment': comment,
                            'rating': rating,
                            'language': lang,
                            'source': urlparse(self.url).netloc.split('.')[1],
                            'author': item.find('div', {'onclick': "widgetEvCall('handlers.usernameClick', event, this);"}).text.strip() if item.find('div', {'onclick': "widgetEvCall('handlers.usernameClick', event, this);"}) else "",
                            'establishment': f'/api/establishments/{self.establishment}',
                            'settings': f'/api/settings/{self.settings}',
                            'date_review': f"{date_rawt[0]}/{month}/{date_rawt[2]}"
                        }

                        reviews.append(review_data)

                if not self.check_date(reviews[-1]['date_review']):
                    break

                try:
                    next_btn = self.driver.find_element(
                        By.CSS_SELECTOR, "a.nav.next")
                    disable_btn = 'disabled' in next_btn.get_attribute(
                        'class').split()
                    if next_btn and not disable_btn:
                        self.driver.execute_script(
                            "arguments[0].click();", next_btn)
                        time.sleep(2)
                    else:
                        break

                except Exception as e:
                    break

            self.data = reviews

        except Exception as e:
            print("erreur:", e)


class Tripadvisor_FR(Tripadvisor):
    def __init__(self, url: str, establishment: str, settings: str):
        super().__init__(url=url, establishment=establishment, settings=settings)

    def extract(self):
        reviews = []

        time.sleep(10)
        print("Entrée")

        try:
            print("Type 1")
            while True:
                print("Boucle ...")
                page = self.driver.page_source

                soupe = BeautifulSoup(page, 'lxml')

                try:

                    reviews_card = soupe.find_all(
                        'div', {'data-test-target': "HR_CC_CARD"})

                    if len(reviews_card):

                        print("reviews_card trouvés!!!")

                        for item in reviews_card:

                            to_save = True

                            title = item.find('div', {'data-test-target': 'review-title'}).text.strip(
                            ) if item.find('div', {'data-test-target': 'review-title'}) else ''

                            detail = item.find('span', {'class': 'QewHA'}).find('span').text.strip(
                            ).replace('\n', '') if item.find('span', {'class': 'QewHA'}) else ''

                            comment = f"{title}{': ' if title and detail else ''}{detail}"

                            try:
                                lang = detect(comment)
                            except:
                                lang = 'fr'

                            year = datetime.today().year
                            month = datetime.today().month
                            day = datetime.today().day

                            date_raw = item.find(
                                'div', {'class': 'cRVSd'}).text.strip() if item.find(
                                'div', {'class': 'cRVSd'}) else ''

                            if date_raw:
                                date_raw_withp = date_raw.split()[-2:]

                                if date_raw_withp[1][0] == '(':
                                    if date_raw_withp[1] == "(Aujourd'hui)":
                                        day = datetime.today().day
                                    elif date_raw_withp[1] == "(Hier)":
                                        day = datetime.today().day - 1
                                else:
                                    if date_raw_withp[0][1:].isnumeric():
                                        day = int(date_raw_withp[0][1:])
                                        month = month_number(
                                            date_raw_withp[1][:-1], 'fr', 'short')
                                    else:
                                        month = month_number(
                                            date_raw_withp[0][1:], 'fr', 'short')
                                        year = date_raw_withp[1][:-1]

                            author = item.find('a', class_='ui_header_link').text.strip(
                            ) if item.find('a', class_='ui_header_link') else "",

                            to_save = date_raw != '' and author != ''

                            review_data = {
                                'comment': comment,
                                'rating': str(int(item.find('span', class_='ui_bubble_rating')['class'][1].split('_')[1]) / 10) + "/5" if item.find('span', class_='ui_bubble_rating') else "0/5",
                                'language': lang,
                                'source': urlparse(self.url).netloc.split('.')[1],
                                'author': author,
                                'establishment': f'/api/establishments/{self.establishment}',
                                'settings': f'/api/settings/{self.settings}',
                                'date_review': f"{day}/{month}/{year}"
                            }

                            to_save and reviews.append(review_data)

                    else:
                        print("Review card non trouvé, tenter autrement ...")
                        raise Exception()

                except:
                    print("Type 2")
                    reviews_card = soupe.find_all(
                        'div', {'class': "review-container"})

                    for item in reviews_card:
                        to_save = True

                        title = item.find('a', {'class': 'title'}).text.strip(
                        ) if item.find('a', {'class': 'title'}) else ''
                        detail = item.find(
                            'div', {'data-prwidget-name': 'reviews_text_summary_hsx'}).text.strip() if item.find(
                            'div', {'data-prwidget-name': 'reviews_text_summary_hsx'}) else ''

                        comment = f"{title}{': ' if title and detail else ''}{detail}"

                        try:
                            lang = detect(comment)
                        except:
                            lang = 'en'

                        rating_bubble = item.find(
                            'span', {'class': 'ui_bubble_rating'})['class'][1]

                        rating = str(
                            int(int(rating_bubble.split('_')[1])/10)) + '/5'

                        date_raw = item.find(
                            'span', {'class': 'ratingDate'})['title']

                        if date_raw != '':
                            date_rawt = date_raw.split()
                            month = month_number(date_rawt[1], 'fr', '')

                        author = item.find('div', {'onclick': "widgetEvCall('handlers.usernameClick', event, this);"}).text.strip(
                        ) if item.find('div', {'onclick': "widgetEvCall('handlers.usernameClick', event, this);"}) else ""

                        to_save = date_raw != '' and author != ''

                        review_data = {
                            'comment': comment,
                            'rating': rating,
                            'language': lang,
                            'source': urlparse(self.url).netloc.split('.')[1],
                            'author': author,
                            'establishment': f'/api/establishments/{self.establishment}',
                            'settings': f'/api/settings/{self.settings}',
                            'date_review': f"{date_rawt[0]}/{month}/{date_rawt[2]}"
                        }

                        to_save and reviews.append(review_data)

                if not self.check_date(reviews[-1]['date_review']):
                    break

                try:
                    next_btn = self.driver.find_element(
                        By.CSS_SELECTOR, "a.nav.next")
                    disable_btn = 'disabled' in next_btn.get_attribute(
                        'class').split()
                    if next_btn and not disable_btn:
                        self.driver.execute_script(
                            "arguments[0].click();", next_btn)
                        time.sleep(2)
                    else:
                        break

                except Exception as e:
                    break

            self.data = reviews

        except:
            print("Type 3")

            while True:
                print("Boucle ...")
                time.sleep(5)
                page = self.driver.page_source

                soupe = BeautifulSoup(page, 'lxml')

                reviews_card = soupe.find_all(
                    'div', {'data-automation': "reviewCard"})

                if len(reviews_card):

                    print("reviews_card trouvés!!!")
                    print(len(reviews_card))

                    for item in reviews_card:

                        to_save = True

                        rating_bubble = item.find(
                            'svg', {'class': 'UctUV d H0'})['aria-label']
                        rating = str(
                            int(rating_bubble.split(',')[0])) + '/5'

                        author = item.find(
                            'a', {'class': 'BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS'}).text.strip() if item.find(
                            'a', {'class': 'BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS'}) else ''

                        title = item.find(
                            'div', {'class': 'biGQs _P fiohW qWPrE ncFvv fOtGX'}).text.strip() if item.find(
                            'div', {'class': 'biGQs _P fiohW qWPrE ncFvv fOtGX'}) else ''

                        comment = item.find(
                            'div', {'class': '_T FKffI'}).text.strip() if item.find(
                            'div', {'class': '_T FKffI'}) else ''

                        comment = f"{title}{': ' if title and comment else ''}{comment}"

                        try:
                            lang = detect(comment)
                        except:
                            lang = 'fr'

                        year = datetime.today().year
                        month = datetime.today().month
                        day = datetime.today().day

                        date_raw = item.find(
                            'div', {'class': 'RpeCd'}).text.strip() if item.find(
                            'div', {'class': 'RpeCd'}) else ''

                        if date_raw:

                            date_raw_withp = date_raw.split(' • ')[0].split()

                            if date_raw_withp[1][0] == '(':
                                if date_raw_withp[1] == "(Aujourd'hui)":
                                    day = datetime.today().day
                                elif date_raw_withp[1] == "(Hier)":
                                    day = datetime.today().day - 1
                            else:
                                if date_raw_withp[0].isnumeric():
                                    day = int(date_raw_withp[0])
                                    month = month_number(
                                        date_raw_withp[1], 'fr', 'short')
                                else:
                                    month = month_number(
                                        date_raw_withp[0], 'fr', 'short')
                                    year = date_raw_withp[1]

                        if author == '' or comment == '' or date_raw == '':
                            to_save = False

                        to_save and reviews.append({
                            'comment': comment,
                            'rating': rating,
                            'language': lang,
                            'source': urlparse(self.url).netloc.split('.')[1],
                            'author': author,
                            'establishment': f'/api/establishments/{self.establishment}',
                            'settings': f'/api/settings/{self.settings}',
                            'date_review': f"{day}/{month}/{year}",
                            'date_visit': f"{day}/{month}/{year}",
                            'novisitday': "1"
                        })

                else:
                    print("Review card non trouvé, Arret !!!")

                if len(reviews) and not self.check_date(reviews[-1]['date_review']):
                    break

                try:
                    next_btn = self.driver.find_element(
                        By.XPATH, "//a[@data-smoke-attr='pagination-next-arrow']")

                    if next_btn:
                        self.driver.execute_script(
                            "arguments[0].click();", next_btn)
                        time.sleep(2)
                    else:
                        break

                except Exception as e:
                    break

            self.data = reviews


# trp = Tripadvisor_FR(
#     url="https://www.tripadvisor.fr/Attraction_Review-g3520917-d518281-Reviews-Courchevel-Saint_Bon_Tarentaise_Courchevel_Savoie_Auvergne_Rhone_Alpes.html", establishment=33, settings=1)
# trp.execute()
# print(trp.data)
