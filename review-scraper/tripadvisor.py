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
    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, settings=settings, env=env, force_refresh=True)

        #### Load all selectors ####

        selector_path = path.join(path.dirname(__file__), 'tripadvisor.json')
        with open(selector_path, 'r') as f:
            self.selectors = json.load(f)

        #### End ####

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

        # input("Continuer...")

        try:
            while True:
                page = self.driver.page_source

                soupe = BeautifulSoup(page, 'lxml')

                review_cards = self.find_soup_element(soupe, 'card', True)

                if (len(review_cards)):

                    for item in review_cards:
                        print("\n--------------- xxx ---------------\n")
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

                        if author:
                            print("author: ", author.text.strip())

                        if rating:
                            print("rating: ", rating.find(
                                'title').text.strip())

                        if title:
                            print("title: ", title.text.strip())

                        if detail:
                            print("detail: ", detail)

                        if review_date:
                            print("review date: ", review_date.text.strip())

                        if visit_date:
                            print("visit date: ", visit_date.text.strip())

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

                # try:

                #     reviews_card = soupe.find_all(
                #         'div', {'data-test-target': "HR_CC_CARD"})

                #     if len(reviews_card) > 0:
                #         print(len(reviews_card))

                #         for item in reviews_card:

                #             to_save = True

                #             title = item.find('div', {'data-test-target': 'review-title'}).text.strip(
                #             ) if item.find('div', {'data-test-target': 'review-title'}) else ''

                #             detail = item.find('span', {'class': 'QewHA'}).find('span').text.strip(
                #             ).replace('\n', '') if item.find('span', {'class': 'QewHA'}) else ''

                #             comment = f"{title}{': ' if title and detail else ''}{detail}"

                #             try:
                #                 lang = detect(comment)
                #             except:
                #                 lang = 'fr'

                #             year = datetime.today().year
                #             month = datetime.today().month
                #             day = datetime.today().day

                #             date_raw = item.find(
                #                 'div', {'class': 'cRVSd'}).text.strip() if item.find(
                #                 'div', {'class': 'cRVSd'}) else ''

                #             if date_raw:
                #                 date_raw_withp = date_raw.split()[-2:]

                #                 if date_raw_withp[1][0] == '(':
                #                     if date_raw_withp[1] == "(Aujourd'hui)":
                #                         day = datetime.today().day
                #                     elif date_raw_withp[1] == "(Hier)":
                #                         day = datetime.today().day - 1
                #                 else:
                #                     if date_raw_withp[0][1:].isnumeric():
                #                         day = int(date_raw_withp[0][1:])
                #                         month = month_number(
                #                             date_raw_withp[1][:-1], 'fr', 'short')
                #                     else:
                #                         month = month_number(
                #                             date_raw_withp[0][1:], 'fr', 'short')
                #                         year = date_raw_withp[1][:-1]

                #             author = item.find('a', class_='ui_header_link').text.strip(
                #             ) if item.find('a', class_='ui_header_link') else "",

                #             to_save = date_raw != '' and author != ''

                #             review_data = {
                #                 'comment': comment,
                #                 'rating': str(int(item.find('span', class_='ui_bubble_rating')['class'][1].split('_')[1]) / 10) + "/5" if item.find('span', class_='ui_bubble_rating') else "0/5",
                #                 'language': lang,
                #                 'source': urlparse(self.url).netloc.split('.')[1],
                #                 'author': ''.join(author),
                #                 'establishment': f'/api/establishments/{self.establishment}',
                #                 'settings': f'/api/settings/{self.settings}',
                #                 'date_review': f"{day}/{month}/{year}",
                #                 'date_visit': f"{day}/{month}/{year}",
                #                 'novisitday': "1"
                #             }

                #             to_save and reviews.append(review_data)

                #     else:
                #         print("Review card non trouvé, tenter autrement ...")
                #         raise Exception()

                # except Exception as e:
                #     print(e)
                # reviews_card = soupe.find_all(
                #     'div', {'class': "review-container"})

                # for item in reviews_card:
                #     to_save = True

                #     title = item.find('a', {'class': 'title'}).text.strip(
                #     ) if item.find('a', {'class': 'title'}) else ''
                #     detail = item.find(
                #         'div', {'data-prwidget-name': 'reviews_text_summary_hsx'}).text.strip() if item.find(
                #         'div', {'data-prwidget-name': 'reviews_text_summary_hsx'}) else ''

                #     comment = f"{title}{': ' if title and detail else ''}{detail}"

                #     try:
                #         lang = detect(comment)
                #     except:
                #         lang = 'en'

                #     rating_bubble = item.find(
                #         'span', {'class': 'ui_bubble_rating'})['class'][1]

                #     rating = str(
                #         int(int(rating_bubble.split('_')[1])/10)) + '/5'

                #     date_raw = item.find(
                #         'span', {'class': 'ratingDate'})['title']

                #     if date_raw != '':
                #         date_rawt = date_raw.split()
                #         month = month_number(date_rawt[1], 'fr', '')

                #     author = item.find('div', {'onclick': "widgetEvCall('handlers.usernameClick', event, this);"}).text.strip(
                #     ) if item.find('div', {'onclick': "widgetEvCall('handlers.usernameClick', event, this);"}) else ""

                #     to_save = date_raw != '' and author != ''

                #     review_data = {
                #         'comment': comment,
                #         'rating': rating,
                #         'language': lang,
                #         'source': urlparse(self.url).netloc.split('.')[1],
                #         'author': author,
                #         'establishment': f'/api/establishments/{self.establishment}',
                #         'settings': f'/api/settings/{self.settings}',
                #         'date_review': f"{date_rawt[0]}/{month}/{date_rawt[2]}",
                #         'date_visit': f"{date_rawt[0]}/{month}/{date_rawt[2]}",
                #         'novisitday': "1"
                #     }

                #     to_save and reviews.append(review_data)

                # if not self.check_date(reviews[-1]['date_review']):
                #     break

                # try:

                # except Exception as e:
                # break

            self.data = reviews

        except Exception as e:
            print(e)

            # while True:
            #     time.sleep(5)
            #     page = self.driver.page_source

            #     soupe = BeautifulSoup(page, 'lxml')

            #     reviews_card = soupe.find_all(
            #         'div', {'data-automation': "reviewCard"})

            #     if len(reviews_card):

            #         for item in reviews_card:

            #             to_save = True

            #             rating_bubble = item.find(
            #                 'svg', {'class': 'UctUV d H0'})['aria-label']
            #             rating = str(
            #                 int(rating_bubble.split(',')[0])) + '/5'

            #             author = item.find(
            #                 'a', {'class': 'BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS'}).text.strip() if item.find(
            #                 'a', {'class': 'BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS'}) else ''

            #             title = item.find(
            #                 'div', {'class': 'biGQs _P fiohW qWPrE ncFvv fOtGX'}).text.strip() if item.find(
            #                 'div', {'class': 'biGQs _P fiohW qWPrE ncFvv fOtGX'}) else ''

            #             comment = item.find(
            #                 'div', {'class': '_T FKffI'}).text.strip() if item.find(
            #                 'div', {'class': '_T FKffI'}) else ''

            #             comment = f"{title}{': ' if title and comment else ''}{comment}"

            #             try:
            #                 lang = detect(comment)
            #             except:
            #                 lang = 'fr'

            #             year = datetime.today().year
            #             month = datetime.today().month
            #             day = datetime.today().day

            #             date_raw = item.find(
            #                 'div', {'class': 'RpeCd'}).text.strip() if item.find(
            #                 'div', {'class': 'RpeCd'}) else ''

            #             if date_raw:

            #                 date_raw_withp = date_raw.split(' • ')[0].split()

            #                 if date_raw_withp[1][0] == '(':
            #                     if date_raw_withp[1] == "(Aujourd'hui)":
            #                         day = datetime.today().day
            #                     elif date_raw_withp[1] == "(Hier)":
            #                         day = datetime.today().day - 1
            #                 else:
            #                     if date_raw_withp[0].isnumeric():
            #                         day = int(date_raw_withp[0])
            #                         month = month_number(
            #                             date_raw_withp[1], 'fr', 'short')
            #                     else:
            #                         month = month_number(
            #                             date_raw_withp[0], 'fr', 'short')
            #                         year = date_raw_withp[1]

            #             if author == '' or comment == '' or date_raw == '':
            #                 to_save = False

            #             to_save and reviews.append({
            #                 'comment': comment,
            #                 'rating': rating,
            #                 'language': lang,
            #                 'source': urlparse(self.url).netloc.split('.')[1],
            #                 'author': author,
            #                 'establishment': f'/api/establishments/{self.establishment}',
            #                 'settings': f'/api/settings/{self.settings}',
            #                 'date_review': f"{day}/{month}/{year}",
            #                 'date_visit': f"{day}/{month}/{year}",
            #                 'novisitday': "1"
            #             })

            #     else:
            #         print("Review card non trouvé, Arret !!!")
            #         break

            #     # if len(reviews) and not self.check_date(reviews[-1]['date_review']):
            #     #     break

            #     try:
            #         next_btn = self.driver.find_element(
            #             By.XPATH, "//a[@data-smoke-attr='pagination-next-arrow']")

            #         if next_btn:
            #             self.driver.execute_script(
            #                 "arguments[0].click();", next_btn)
            #             time.sleep(2)
            #         else:
            #             break

            #     except Exception as e:
            #         break

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
#     url="https://www.tripadvisor.fr/Attraction_Review-g3520917-d518281-Reviews-Courchevel-Saint_Bon_Tarentaise_Courchevel_Savoie_Auvergne_Rhone_Alpes.html", establishment=33, settings=1)
# trp.execute()
# print(trp.data)
