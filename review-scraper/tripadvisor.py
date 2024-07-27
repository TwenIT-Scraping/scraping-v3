import string
from scraping import Scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException
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
from os import path
import random
import json


class Tripadvisor(Scraping):
    def __init__(self, url: str, establishment: str, settings: str, name:str, env: str):
        super().__init__(in_background=False, url=url, establishment=establishment, settings=settings, env=env, force_refresh=True)

        #### Load all selectors ####
        print("class init start")
        self.name = name
        print(f"name get {self.name}")
        
        selector_path = path.join(path.dirname(__file__), 'tripadvisor.json')
        with open(selector_path, 'r') as f:
            self.selectors = json.load(f)


    # def navigate_random_page(self):
    #     self.driver.get("")

    """Simulation des recherches"""

        #### End ####

    def format_date(self, text, lang, form=1):
        rawt_date = text.split()
        print(rawt_date, lang, form)
        today = datetime.today()

        if lang == 'fr':
            if form == 1 and rawt_date[-3].isnumeric() == False:
                form = 3

            if form == 1:
                month = month_number(
                    rawt_date[-2].replace('(', '').replace(')', ''), lang, '')
                return f"{rawt_date[-3]}/{month}/{rawt_date[-1].replace('(', '').replace(')', '')}"
            if form == 2:
                month = month_number(rawt_date[0].replace(
                    '(', '').replace(')', ''), lang, 'short')
                return f"{today.day}/{month}/{rawt_date[1].replace('(', '').replace(')', '')}"
            if form == 3:
                month = month_number(rawt_date[-2].replace(
                    '(', '').replace(')', ''), lang, 'short')
                return f"{today.day}/{month}/{rawt_date[-1].replace('(', '').replace(')', '')}"
        if lang == 'es':
            if form == 1 and rawt_date[-3].isnumeric() == False:
                form = 3
            if form == 1:
                month = month_number(
                    rawt_date[-2].replace('(', '').replace(')', ''), lang, 'short')
                return f"{rawt_date[-3]}/{month}/{rawt_date[-1].replace('(', '').replace(')', '')}"
            if form == 2:
                month = month_number(
                    rawt_date[-3].replace('(', '').replace(')', ''), lang, '')
                return f"{today.day}/{month}/{rawt_date[-1].replace('(', '').replace(')', '')}"
            if form == 3:
                month = month_number(rawt_date[-2].replace(
                    '(', '').replace(')', ''), lang, 'short')
                return f"{today.day}/{month}/{rawt_date[-1].replace('(', '').replace(')', '')}"
        return

    def extract(self):
        pass

    def find_soup_element(self, soupe, key, all=True):
        elements = None
        element = None
        loop = True
        if key in self.selectors.keys():
            for t in self.selectors[key]["tag"]:
                if not loop:
                    break

                for a in self.selectors[key]["attr"]:
                    if not loop:
                        break

                    for v in self.selectors[key]["value"]:
                        if not loop:
                            break

                        try:
                            if all:
                                elements = soupe.find_all(t, {a: v})
                                if elements and len(elements) > 0:
                                    loop = False
                            else:
                                element = soupe.find(t, {a: v})
                                if (element):
                                    loop = False

                        except Exception as e:
                            pass

        return elements if all else element

    def find_driver_element(self, key, all=True):
        elements = None
        element = None
        loop = True

        if key in self.selectors.keys():
            for t in self.selectors[key]:
                method = By.CSS_SELECTOR if t['type'] == 'css' else By.XPATH
                if not loop:
                    break
                try:
                    if all:
                        elements = self.driver.find_elements(
                            method, t['value'])
                        if elements and len(elements) > 0:
                            loop = False
                    else:
                        element = self.driver.find_element(method, t['value'])
                        if (element):
                            loop = False

                except Exception as e:
                    pass

        return elements if all else element


class Tripadvisor_UK(Tripadvisor):
    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(url=url, establishment=establishment, settings=settings, env=env)

    def extract(self):
        reviews = []

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
                        rating = str(
                            int(int(rating_bubble.split('_')[1])/10)) + '/5'

                        try:
                            date_raw = item.find(
                                'span', {'class': 'ratingDate'})['title']

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
                            'date_review': f"{date_rawt[0]}/{month}/{date_rawt[2]}",
                            'date_visit': f"{date_rawt[0]}/{month}/{date_rawt[2]}",
                            'novisitday': "1"
                        }

                        reviews.append(review_data)

                # if not self.check_date(review_data['date_review']):
                #     break

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
    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(url=url, establishment=establishment, settings=settings, env=env)

    def extract(self):
        reviews = []
        time.sleep(random.randint(5, 25))

        try:
            while True:
                page = self.driver.page_source

                soupe = BeautifulSoup(page, 'lxml')

                review_cards = self.find_soup_element(soupe, 'card', True)

                if (len(review_cards)):

                    for item in review_cards:

                        author = self.find_soup_element(
                            item, 'author', False)
                        rating = self.find_soup_element(
                            item, 'rating', False)
                        title = self.find_soup_element(
                            item, 'title', False)
                        detail = self.find_soup_element(
                            item, 'detail', False)
                        review_date = self.find_soup_element(
                            item, 'review-date', False)
                        visit_date = self.find_soup_element(
                            item, 'visit-date', False)

                        comment = f"{title.text.strip() if title else ''}{': ' if title and detail else ''}{detail.text.strip() if detail else ''}"
                        lang = self.detect(comment)
                        date_lang = self.detect(review_date.text.strip())

                        if lang and date_lang == self.lang:

                            review_data = {
                                'comment': comment.replace('\n', ' '),
                                'rating': rating.find('title').text.strip().split()[0].replace(',', '.')+"/5" if rating else "0/5",
                                'language': lang,
                                'source': urlparse(self.url).netloc.split('.')[1],
                                'author': author.text.strip() if author else "",
                                'establishment': f'/api/establishments/{self.establishment}',
                                'settings': f'/api/settings/{self.settings}',
                                'date_review': self.format_date(review_date.text.strip(), date_lang, 1) if review_date else '',
                                'date_visit': self.format_date(visit_date.text.strip(), date_lang, 2) if visit_date else '',
                                'novisitday': "1"
                            }

                            print(review_data)

                            to_save = review_date != '' and author != '' and visit_date != '' and lang == self.lang

                            if to_save:
                                reviews.append(review_data)
                            else:
                                print("not saved:")
                                print("\t", review_date, "\n")
                                print("\t", comment, "\n")
                                print("\t", rating, "\n")
                                print("\t", author, "\n")
                                print("\t", visit_date, "\n")
                                print("\t", lang, '|', self.lang, "\n")

                if len(reviews) and (datetime.strptime(reviews[-1]["date_review"], "%d/%m/%Y") < datetime.today()-timedelta(days=365)):
                    break

                next_btn = self.find_driver_element(
                    "next", False)

                if next_btn:
                    disable_btn = 'disabled' in next_btn.get_attribute(
                        'class').split()

                    if not disable_btn:
                        try:
                            print("navigate to next page...")
                            self.driver.execute_script(
                                "arguments[0].click();", next_btn)

                            time.sleep(random.randint(1, 20))
                        except Exception as e:
                            print(e)
                            pass

                    else:
                        break

                else:
                    break

        except Exception as e:
            print(e)

        self.data = reviews


class Tripadvisor_ES(Tripadvisor):
    def __init__(self, url: str, establishment: str, settings: str, env: str):
        url = url.replace(".fr/", ".es/")
        super().__init__(url=url, establishment=establishment, settings=settings, env=env)

    def extract(self):
        def get_next_btn_element() -> object:
            try:
                return self.driver.find_element(By.CSS_SELECTOR, "a.ui_button.nav.next.primary")
            except NoSuchElementException:
                return self.driver.find_element(By.XPATH, "//a[@data-smoke-attr='pagination-next-arrow']")

        reviews = []

        # time.sleep(30)
        input("Appuiez sur la touche entrée pour continuer ...")

        try:
            while True:
                print("==== Extracting ... ====")
                page = self.driver.page_source

                soupe = BeautifulSoup(page, 'lxml')

                try:

                    reviews_card = soupe.find_all(
                        'div', {'data-test-target': "HR_CC_CARD"})

                    print("**** Card trouvé: ", len(reviews_card), " ****")

                    if len(reviews_card) > 0:

                        for item in reviews_card:

                            to_save = True

                            title = item.find('div', {'data-test-target': 'review-title'}).text.strip(
                            ) if item.find('div', {'data-test-target': 'review-title'}) else ''

                            detail = item.find('span', {'class': 'orRIx'}).find('span').text.strip(
                            ).replace('\n', '') if item.find('span', {'class': 'orRIx'}) else ''

                            comment = f"{title}{': ' if title and detail else ''}{detail}"

                            try:
                                lang = detect(comment)
                            except:
                                lang = 'es'

                            year = datetime.today().year
                            month = datetime.today().month
                            day = datetime.today().day

                            links = item.find_all(
                                "a", href=lambda href: href and "Profile" in href)
                            author_link = [
                                link for link in links if link.text.strip() != ""]

                            author = author_link[0].text.strip() if len(
                                author_link) > 0 else ""

                            date_raw = author_link[0].parent.text.strip() if len(
                                author_link) > 0 else ""

                            if date_raw:
                                date_raw_withp = date_raw.split()[-2:]

                                if date_raw_withp[1][0] == '(':
                                    if date_raw_withp[1] == "(hoy)":
                                        day = datetime.today().day
                                    elif date_raw_withp[1] == "(ayer)":
                                        day = datetime.today().day - 1
                                else:
                                    if date_raw_withp[0][1:].isnumeric():
                                        day = int(date_raw_withp[0][1:])
                                        month = month_number(
                                            date_raw_withp[1][:-1], 'es', 'short')
                                    else:
                                        month = month_number(
                                            date_raw_withp[0][1:], 'es', 'short')
                                        year = date_raw_withp[1][:-1]

                            to_save = date_raw != '' and author != ''

                            print("A sauvegarder: ", to_save)
                            print("informations initiales: ", date_raw, author)

                            review_data = {
                                'comment': comment,
                                'rating': str(int(item.find('div', {'data-test-target': 'review-rating'}).find('svg').find('title').text.strip().split(' ')[0].split(',')[0]))+"/5"
                                if item.find('div', {'data-test-target': 'review-rating'})
                                and item.find('div', {'data-test-target': 'review-rating'}).find('svg')
                                and item.find('div', {'data-test-target': 'review-rating'}).find('svg').find('title') else "0/5",
                                'language': lang,
                                'source': 'tripadvisor',
                                'author': ''.join(author),
                                'establishment': f'/api/establishments/{self.establishment}',
                                'settings': f'/api/settings/{self.settings}',
                                'date_review': f"{day}/{month}/{year}",
                                'date_visit': f"{day}/{month}/{year}",
                                'novisitday': "1"
                            }

                            print(review_data)

                            to_save and reviews.append(review_data)
                            print("====> nombre reviews à l'instant: ",
                                  len(reviews))

                        # if not self.check_date(review_data['date_review']):
                        #     print("!!!!!!!!!!!!!! Date dépassée !!!!!!!!!!!!!!")
                        #     break

                    else:
                        print("!!!!!!!!!!!! Pas de card trouvé !!!!!!!!!!!!!!!")
                        raise Exception("Aucun card trouvé!!!")

                    try:
                        print("***** Pass to next page ...")
                        next_btn = get_next_btn_element()

                        if next_btn:
                            print("=> Click to next...")
                            try:
                                next_btn.click()
                            except:
                                self.driver.execute_script(
                                    "arguments[0].click();", next_btn)
                                time.sleep(random.randint(3, 10))
                        else:
                            print("=> Next button not found!")
                            break

                    except Exception as e:
                        print("////// Error when passing to next page...")
                        print(e)
                        break
                except Exception as e:
                    print("Exception niveau 2:")
                    print(e)
                    pass

        except Exception as e:
            print("Exception niveau 1:")
            print(e)

        print("<=============> Nombre reviews final: ",
              len(reviews), "<============>")

        self.data = reviews


# trp = Tripadvisor_FR(
#     url="https://www.tripadvisor.fr/Attraction_Review-g3520917-d518281-Reviews-Courchevel-Saint_Bon_Tarentaise_Courchevel_Savoie_Auvergne_Rhone_Alpes.html", establishment=33, settings=1, env='DEV')
# trp.execute()
# print(trp.data)

# Écrit le 28 février 2019
        # févr. 2019 • En couple
        # Fecha de la estancia: octubre de 2023
        # Respondido el 4 mar 2024
