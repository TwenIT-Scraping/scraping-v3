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


class Trustpilot(Scraping):
    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, settings=settings, env=env)

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

        while True:

            page = self.driver.page_source

            soupe = BeautifulSoup(page, 'lxml')
            base_url = "https://fr.trustpilot.com"

            review_cards = soupe.find_all(
                'article', {'data-service-review-card-paper': "true"})
            

            for card in review_cards:
                title = card.find('a', {'data-review-title-typography': 'true'}).text.strip(
                ) if card.find('a', {'data-review-title-typography': 'true'}) else ""
                detail = card.find('p', {'data-service-review-text-typography': 'true'}).text.strip(
                ) if card.find('p', {'data-service-review-text-typography': 'true'}) else ""
                comment = f"{title}{': ' if title and detail else ''}{detail}"

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

                url = ''
                try:
                    url = base_url + card.find('a', {'class':"link_internal__7XN06 typography_appearance-default__AAY17 typography_color-inherit__TlgPO link_link__IZzHN link_notUnderlined__szqki"},href=True)['href']
                except:
                    pass

                date_review != "01/01/1999" and reviews.append({
                    'comment': comment,
                    'rating': card.find('div', {'data-service-review-rating': True})['data-service-review-rating'] if card.find('div', {'data-service-review-rating': True}) else "0",
                    'date_review': date_review,
                    'language': lang,
                    'url': url,
                    'source': urlparse(self.url).netloc.split('.')[1],
                    'author': card.find('span', {'data-consumer-name-typography': 'true'}).text.strip() if card.find('span', {'data-consumer-name-typography': 'true'}) else "",
                    'establishment': f'/api/establishments/{self.establishment}',
                    'settings': f'/api/settings/{self.settings}',
                    'date_visit': date_review,
                    'novisitday': "1"
                })

            if not self.check_date(reviews[-1]['date_review']):
                break

            try:
                next_btn = self.driver.find_element(
                    By.NAME, 'pagination-button-next')
                disabled_btn = True if next_btn.get_attribute(
                    'aria-disabled') else False

                if next_btn and not disabled_btn:
                    self.driver.execute_script(
                        "arguments[0].click();", next_btn)
                    time.sleep(4)
                else:
                    break

            except Exception as e:
                break
                # print(e)

        self.data = reviews


# trp = Trustpilot(url="https://fr.trustpilot.com/review/liberkeys.com")
# trp.execute()
# print(trp.data)
