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

#format date 05 08 2025
def format_date_fr(date_str:str) -> str:
    # input(f'date_str => {date_str}')
    # 28 juin 2023
    month_fr = {
    "janvier": "01",  
    "février": "02",  
    "mars": "03",  
    "avril": "04",  
    "mai": "05",  
    "juin": "06",  
    "juillet": "07",  
    "août": "08",  
    "septembre": "09",  
    "octobre": "10",  
    "novembre": "11",  
    "décembre": "12" 
    }
    date_str = date_str.lower().split(' ')
    if len(date_str) == 3:
        # input(f" date formatté => {date_str[0]}/{month_fr[date_str[1]]}/{date_str[2]}")
        return f"{date_str[0]}/{month_fr[date_str[1]]}/{date_str[2]}"

class Trustpilot(Scraping):
    def __init__(self, url: str, establishment: str, settings: str, env: str, last_review_date : str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, settings=settings, env=env, last_review_date=last_review_date)

    def extract(self):

        reviews = []

        time.sleep(2)
        sort_btn = self.driver.find_element(
            By.XPATH, "//button[@name='sort' and @data-sort-button='true']")

        try:
            element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, "//input[@value='recency']")))

            element.click()
        except Exception as e:
            print(e)

        time.sleep(5)

        # while True:

        #     page = self.driver.page_source

        #     soupe = BeautifulSoup(page, 'lxml')
        #     base_url = "https://fr.trustpilot.com"

        #     review_cards = soupe.find_all(
        #         'article', {'data-service-review-card-paper': "true"})
            

        #     for card in review_cards:
        #         title = card.find('a', {'data-review-title-typography': 'true'}).text.strip(
        #         ) if card.find('a', {'data-review-title-typography': 'true'}) else ""
        #         detail = card.find('p', {'data-service-review-text-typography': 'true'}).text.strip(
        #         ) if card.find('p', {'data-service-review-text-typography': 'true'}) else ""
        #         comment = f"{title}{': ' if title and detail else ''}{detail}"

        #         try:
        #             lang = detect(comment)
        #         except:
        #             lang = 'en'

        #         raw_date = card.find(
        #             'time')['datetime'] if card.find('time') else ""
        #         if raw_date:
        #             date_review = '/'.join([raw_date[8:10],
        #                                    raw_date[5:7], raw_date[0:4]])
        #         else:
        #             date_review = "01/01/1999"

        #         url = ''
        #         try:
        #             url = base_url + card.find('a', {'class':"link_internal__7XN06 typography_appearance-default__AAY17 typography_color-inherit__TlgPO link_link__IZzHN link_notUnderlined__szqki"},href=True)['href']
        #         except:
        #             pass

        #         date_review != "01/01/1999" and reviews.append({
        #             'comment': comment,
        #             'rating': card.find('div', {'data-service-review-rating': True})['data-service-review-rating'] if card.find('div', {'data-service-review-rating': True}) else "0",
        #             'date_review': date_review,
        #             'language': lang,
        #             'url': '',
        #             'source': urlparse(self.url).netloc.split('.')[1],
        #             'author': card.find('span', {'data-consumer-name-typography': 'true'}).text.strip() if card.find('span', {'data-consumer-name-typography': 'true'}) else "",
        #             'establishment': f'/api/establishments/{self.establishment}',
        #             'settings': f'/api/settings/{self.settings}',
        #             'date_visit': date_review,
        #             'novisitday': "1"
        #         })

        #     if not self.check_date(reviews[-1]['date_review'], self.last_review_date):
        #         break

        #     try:
        #         next_btn = self.driver.find_element(
        #             By.NAME, 'pagination-button-next')
        #         disabled_btn = True if next_btn.get_attribute(
        #             'aria-disabled') else False

        #         if next_btn and not disabled_btn:
        #             self.driver.execute_script(
        #                 "arguments[0].click();", next_btn)
        #             time.sleep(4)
        #         else:
        #             break

        #     except Exception as e:
        #         break
        #         # print(e)

        #debut code 29 07 2025
        break_transmetter = True
        while break_transmetter:

            page = self.driver.page_source

            soupe = BeautifulSoup(page, 'lxml')
            base_url = "https://fr.trustpilot.com"

            review_container = soupe.find('div', {'class': 'styles_wrapper__ie3f0'}) #21 01 2026

            review_cards = review_container.find_all('div', {'class': "styles_cardWrapper__g8amG styles_show__Z8n7u"})
            
            for card in review_cards:
                title = card.find('h2', {'data-service-review-title-typography': 'true'}).text.strip(
                ) if card.find('h2', {'data-service-review-title-typography': 'true'}) else ""
                # input(f'Title => {title}')
                detail = card.find('p', {'data-service-review-text-typography': 'true'}).text.strip(
                ) if card.find('p', {'data-service-review-text-typography': 'true'}) else ""
                comment = f"{title}{': ' if title and detail else ''}{detail}"
                # input(f"comment => {comment}")

                try:
                    lang = detect(comment)
                except:
                    lang = 'en'

                raw_date = card.find(
                    'time')['datetime'] if card.find('time') else ""
                if raw_date:
                    date_review = '/'.join([raw_date[8:10],
                                           raw_date[5:7], raw_date[0:4]])
                else:
                    date_review = "01/01/1999"

                #pour date visite car date visite n'est pas forcémment = à la date_review ce qu'a fait l'ancien code
                try:
                    # date_visit_not_formatted = card.find('p', {'data-service-review-date-of-experience-typography': 'true'}).find('span').text.strip()
                    #MAJ 21 08 2025 
                    date_visit_not_formatted = card.find('div', {'data-testid': 'review-badge-date'}).find('span').text.strip()
                    # input(f'date_visit_not_formatted => {date_visit_not_formatted}')
                    date_visit_formatted = format_date_fr(date_visit_not_formatted)
                    # input(f'date_visit_formatted => {date_visit_formatted}')
                except:
                    input('dans au niveau de la date visit')
                url = ''
                try:
                    url = base_url + card.find('a', {'class':"link_internal__Eam_b link_wrapper__ahpyq styles_consumerDetails__POC79"},href=True)['href']
                except:
                    print('pas de lien')
                    url = self.driver.current_url
                    input(f"url global car url spécifique non existante => {url}")
                    pass
                
                if date_review != "01/01/1999" :
                    reviews.append({
                        'comment': comment,
                        'rating': card.find('div', {'data-service-review-rating': True})['data-service-review-rating'] if card.find('div', {'data-service-review-rating': True}) else "0",
                        'date_review': date_review,
                        'language': lang,
                        'url': url,
                        'source': urlparse(self.url).netloc.split('.')[1],
                        'author': card.find('span', {'data-consumer-name-typography': 'true'}).text.strip() if card.find('span', {'data-consumer-name-typography': 'true'}) else "",
                        'establishment': f'/api/establishments/{self.establishment}',
                        'settings': f'/api/settings/{self.settings}',
                        'date_visit': date_visit_formatted,
                        'novisitday': "1"
                    })

                # input(f'on a {len(reviews)} reviews a faire entrés dans la base de données')
                # input(f"date du dernier review appender => {reviews[-1]['date_review']} et date du dernier dans la base => {self.last_review_date}")
            # input(f"date du dernier review appender => {reviews[-1]['date_review']} et date du dernier dans la base => {self.last_review_date}")
            #26 01 2026 :ajustement condition pour condition si nouvel établissement
            if self.last_review_date != None:
                print('last review is NOT NONE')
                if datetime.strptime(reviews[-1]['date_review'],'%d/%m/%Y') >= datetime.strptime(self.last_review_date,'%d/%m/%Y'):
                    print('Review encore à prendre')
                    break_transmetter = True
                elif datetime.strptime(reviews[-1]['date_review'],'%d/%m/%Y') < datetime.strptime(self.last_review_date,'%d/%m/%Y'):
                    print(" Date review atteinte, break du for")
                    break_transmetter = False
                    # print(f"last review date => 05/01/2025 > {reviews[-1]['date_review']} DONC on ne clique plus au next reviews page" )
                    break
            elif self.last_review_date == None: #nouvel établissement sans review encore
                print('last review is NONE')
                if datetime.strptime(reviews[-1]['date_review'],'%d/%m/%Y') >= (datetime.now() - timedelta(days=365)):
                    print(f"date du dernier review sur la page => {reviews[-1]['date_review']} >>>> {datetime.now() - timedelta(days=365)}")
                    break_transmetter = True
                elif datetime.strptime(reviews[-1]['date_review'],'%d/%m/%Y') < (datetime.now() - timedelta(days=365)):
                    print("Date atteinte, break")
                    break_transmetter = False
                    break

            #entre ici lorsque le date de review sur page est encore > last review date
            if break_transmetter:
                # input(f'on a {len(reviews)} reviews a faire entrés dans la base de données et voici ce qu\'il contient => {reviews}')
                #27 01 2026
                clickable = self.driver.find_elements(By.NAME, 'pagination-button-2')
                if clickable:
                    input('NEX BUTTON CLICKABLE')
                else:
                    input('Pas de NEXT BUTTON CLICKABLE')
                    break

                try:
                    next_btn = self.driver.find_element(
                        By.NAME, 'pagination-button-next')
                    disabled_btn = True if next_btn.get_attribute(
                        'aria-disabled') else False

                    if next_btn and not disabled_btn:
                        print('Date review sur page > last date en base, page suivante')
                        self.driver.execute_script(
                            "arguments[0].click();", next_btn)
                        print("clique sur le next button")
                        time.sleep(2)
                    else:
                        input("clique next button non effectué")

                except Exception as e:
                    input(f'erreur clique button next for other reviews => {e}, check navigator si besoin')
                    pass
            else:
                break

        self.data = reviews


# trp = Trustpilot(url="https://fr.trustpilot.com/review/liberkeys.com")
# trp.execute()
# print(trp.data)

