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
import random
from tools import month_number

months_es_short = {
    'ene': '01',
    'feb': '02',
    'mar': '03',
    'abr': '04',
    'may': '05',
    'jun': '06',
    'jul': '07',
    'ago': '08',
    'sept': '09',
    'oct': '10',
    'nov': '11',
    'dic': '12'
}

class Expedia(Scraping):
    def __init__(self, url: str, establishment: str, settings: str, env: str):
        url_split = url.split('.')
        url_split[-1] = 'Avis-Voyageurs'
        url = '.'.join(url_split)

        super().__init__(in_background=False, url=url,
                         establishment=establishment, settings=settings, env=env)

    def load_reviews(self):
        # time.sleep(5)
        print("\n Loading ... \n")

        #Ajout d'une instruction qui clique sur le bouton / lien qui est en charge d'afficher les reviews car il n'y en avait paset c'est pour ça qu'on a rien
        time.sleep(3)
        print('CLIQUE SUR LE BOUTON')
        button_show_reviews = self.driver.find_element(By.CSS_SELECTOR, "button[data-stid='reviews-link']")
        if button_show_reviews:
            self.driver.execute_script("arguments[0].click();", button_show_reviews)

        time.sleep(3)

        def get_last_review_date():
            page = self.driver.page_source
            time.sleep(5) #attendre un peut l'url car desfois on a une erreur
            soupe = BeautifulSoup(page, 'lxml')
            """ Nouveau code 03 10 2024 """
            try:
                
                last_review_cards = soupe.find('div', {'class', 'uitk-card uitk-card-roundcorner-all uitk-card-has-primary-theme'}).find_all('article', {'itemprop':'review'})[-1]
                return self.find_review_date(last_review_cards)
            except Exception as e:
                print(f'Erreur dans load_review() au niveau de sa fonction get_last_review_date() ==> {e}')
            """ Fin Nouveau code 03 10 2024 """
            

        while True:
            time.sleep(random.randint(1, 3))

            if not self.check_date(get_last_review_date()):
                print('On a zappé un review car la date ne correspond pas à notre condition')
                break

            try:
                #j'ai changé en nom de variable plus explicite le next_btn en button_more_reviews
                button_more_reviews = self.driver.find_elements(
                    By.CSS_SELECTOR, '.uitk-button.uitk-button-medium.uitk-button-has-text.uitk-button-secondary')

                if len(button_more_reviews) == 2:
                    self.driver.execute_script(
                        "arguments[0].click();", button_more_reviews[1])
                    print('Clique sur More Review car on peut encore scrapé les autres dates ')
                    time.sleep(random.randint(1, 3))
                else:
                    break

            except Exception as e:
                print(f'Erreur dans la méthode load_review() de Expedia, dans le bloque de clique sur more review => {e}')
                break

    def find_review_date(self, card):
        date_raw = card.find('span', {'itemprop': 'datePublished'}).text.strip(
        ) if card.find('span', {'itemprop': 'datePublished'}) else ""

        """ Nouveau code 03 10 2024 """
        if 'expedia.es' in self.driver.current_url:
            print('Type de date en langue ES')
            date_split = date_raw.split(' ') #on a ici 0 à 4 dans date split car il y a les "de"
            day = date_split[0]
            month = months_es_short[date_split[2]]
            year = date_split[4]
            date_review = f'{day}/{month}/{year}'
            return date_review
        else:
            """ Fin nouveau code 03 10 2024 """

            try:
                date_review = datetime.strftime(datetime.strptime(
                    date_raw, '%d %b %Y'), '%d/%m/%Y') if date_raw else "01/01/1999" 
                print(f'date review = {date_review}')
            except:
                date_rawt = date_raw.split()
                date_review = "%s/%s/%s" % (date_rawt[0], month_number(
                    date_rawt[1], 'fr', 'short'), date_rawt[2])

            return date_review

    def extract(self):
        """ On active ça seulement lors des debug mais je vais enlever le caractère pour plus de rapidité
        enter_key = str(input("Entrer un caractère svp:"))"""
        run_the_code = True
        time.sleep(3)
        if run_the_code:

            self.load_reviews()

            reviews = []

            print("\n Extraction ... \n")

            page = self.driver.page_source

            soupe = BeautifulSoup(page, 'lxml')
            
            """ Nouveau code 03 10 2024 (Pour infos : Expedia aussi a des 'read more' sur les reviews mais pour leur cas tout est affiché dans l'html, donc pas besoin de cliquer)"""
            try:
                
                review_cards = soupe.find('div', {'class', 'uitk-card uitk-card-roundcorner-all uitk-card-has-primary-theme'}).find_all('article', {'itemprop':'review'})
                
            except Exception as e:
                print(f'ERREUR dans extract() de la classe Expedia ==> {e}')
            """ Nouveau code 03 10 2024 """

            for card in review_cards:
                title = card.find('span', {'itemprop': 'name'}).text.strip(
                ) if card.find('span', {'itemprop': 'name'}) else ""
                detail = card.find('span', {'itemprop': 'description'}).text.strip(
                ) if card.find('span', {'itemprop': 'description'}) else ""
                comment = f"{title}{': ' if title and detail else ''}{detail}"

                try:
                    lang = detect(comment)
                except:
                    lang = 'en'

                date_review = self.find_review_date(card)

                try:
                    t = {
                        'comment': comment,
                        'rating': card.find('span', {'itemprop': 'ratingValue'}).text.strip().split('/')[0] + "/10"
                        if card.find('span', {'itemprop': 'ratingValue'}) else "0/10",
                        'date_review': date_review,
                        'language': lang,
                        'source': urlparse(self.url).netloc.split('.')[1],
                        'author': card.find('h4').text.strip(),
                        'establishment': f'/api/establishments/{self.establishment}',
                        'settings': f'/api/settings/{self.settings}',
                        'date_visit': date_review,
                        'novisitday': "0",
                        'url' : self.driver.current_url
                    }
                    t['date_review'] != '01/01/1999' and reviews.append(t)
                except Exception as e:
                    print(e)

            self.data = reviews


# trp = Expedia(url="https://www.expedia.com/Les-Deserts-Hotels-Vacanceole-Les-Balcons-DAix.h2481279.Hotel-Reviews")
# trp.execute()
# print(trp.data)
