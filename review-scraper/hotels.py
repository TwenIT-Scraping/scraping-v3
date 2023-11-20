import random
from scraping import Scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from abc import abstractmethod
import sys
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from langdetect import detect
from tools import month_number
from random import randint
from selenium.webdriver.support.select import Select


class Hotels(Scraping):

    def __init__(self, url: str, establishment: str, settings: str):
        url = url + '?pwaDialog=reviews-property-reviews-1'
        super().__init__(in_background=False, url=url,
                         establishment=establishment, settings=settings)

    def close_popup(self) -> None:
        try:
            self.driver.find_element(
                By.CLASS_NAME, 'osano-cm-button--type_accept').click()
        except:
            pass

    def load_reviews(self) -> None:
        self.close_popup()

        for i in range(5):
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

    def extract(self) -> None:
        pass


class Hotels_FR(Hotels):

    def __init__(self, url: str, establishment: str, settings: str):
        super().__init__(url=url, establishment=establishment, settings=settings)

    def format_date(self, date: str) -> str:
        date = date.split(' ')
        month = month_number(date[1], 'fr', 'short')
        return f'{date[0]}/{month}/{date[2]}'

    def load_reviews(self) -> None:
        def get_last_review_date():
            page = self.driver.page_source
            soupe = BeautifulSoup(page, 'lxml')
            review_cards = soupe.find('div', {
                'data-stid': 'property-reviews-list'}).find_all('article', {'itemprop': 'review'})[-1]

            return self.format_date(review_cards.find(
                'span', {'itemprop': 'datePublished'}).text.strip())

        super().load_reviews()

        print("Load reviews ...")

        try:
            self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Afficher tous les avis')]").click()
        except Exception as e:
            print(e)

        time.sleep(3)

        try:
            self.driver.find_element(
                By.XPATH, "//select[@id='sortBy']/option[@value='NEWEST_TO_OLDEST']").click()

            time.sleep(2)

            more_btn = self.driver.find_element(
                By.XPATH, '//button[contains(text(), "Plus d’avis voyageurs")]')

            while more_btn.is_displayed():
                if not self.check_date(get_last_review_date()):
                    break

                more_btn.click()
                WebDriverWait(self.driver, 5)
                time.sleep(1)
        except:
            pass

    def extract(self) -> None:

        reviews = []

        time.sleep(1)

        self.load_reviews()

        time.sleep(random.uniform(.5, 4.0))

        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        review_cards = soup.find('div', {
                                 'data-stid': 'property-reviews-list'}).find_all('article', {'itemprop': 'review'})

        for review in review_cards:
            data = {}
            data['date_review'] = self.format_date(review.find(
                'span', {'itemprop': 'datePublished'}).text.strip())
            data['author'] = review.find('img').parent.text.split(',')[0]
            data['rating'] = review.find('span', {'itemprop': 'ratingValue'}).text.split(
                ' ')[0] if review.find('span', {'itemprop': 'ratingValue'}) else '0'
            data['comment'] = review.find('span', {'itemprop': 'description'}).text if review.find(
                'span', {'itemprop': 'description'}) else ''

            data['language'] = 'fr'

            data['establishment'] = f'/api/establishments/{self.establishment}'
            data['settings'] = f'/api/establishments/{self.settings}'
            data['source'] = urlparse(self.url).netloc.split('.')[1]
            data['date_visit'] = data['date_review']
            data['novisitday'] = "0"

            reviews.append(data)

        self.data = reviews


class Hotels_EN(Hotels):

    def __init__(self, url: str, establishment: str, settings: str):
        super().__init__(url=url, establishment=establishment, settings=settings)

    def load_reviews(self) -> None:
        super().load_reviews()

        print("Load reviews ...")

        try:
            self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Afficher tous les avis')]").click()
        except Exception as e:
            print(e)

        try:
            time.sleep(2)
            button_view_more = self.driver.find_element(By.CSS_SELECTOR, '#app-layer-reviews-property-reviews-1 > section > div.uitk-sheet-content.uitk-sheet-content-padded.uitk-sheet-content-extra-large > div > div.uitk-layout-grid.uitk-layout-grid-align-content-start.uitk-layout-grid-has-auto-columns.uitk-layout-grid-has-columns.uitk-layout-grid-has-space.uitk-layout-grid-display-grid.uitk-layout-grid-item.uitk-layout-grid-item-has-column-start.uitk-layout-grid-item-has-column-start-by-medium.uitk-layout-grid-item-has-column-start-by-large.uitk-layout-grid-item-has-column-start-by-extra_large > div.uitk-layout-grid-item > section > div.uitk-spacing.uitk-type-center.uitk-spacing-margin-block-three > button')
            while button_view_more.is_displayed():
                try:
                    self.driver.find_element(
                        By.CSS_SELECTOR, '#app-layer-recommendations-overlay > section > div.uitk-layout-flex.uitk-layout-flex-align-items-center.uitk-toolbar > button').click()
                except:
                    pass
                button_view_more.click()
                WebDriverWait(self.driver, 5)
                time.sleep(1)
        except:
            pass

    def extract(self) -> None:
        def fomat_date(date: str) -> str:
            date = date.split(' ')
            month = month_number(date[1], 'en', 'short')
            return f'{date[0]}/{month}/{date[2]}'

        reviews = []

        time.sleep(5)

        self.load_reviews()

        # soup = BeautifulSoup(self.driver.page_source, 'lxml')
        # review_cards = soup.find('div', {
        #                          'data-stid': 'property-reviews-list'}).find_all('article', {'itemprop': 'review'})

        # for review in review_cards:
        #     data = {}
        #     data['date_review'] = fomat_date(review.find(
        #         'span', {'itemprop': 'datePublished'}).text.strip())
        #     data['author'] = review.find('img').parent.text.split(',')[0]
        #     data['rating'] = review.find('span', {'itemprop': 'ratingValue'}).text.split(
        #         ' ')[0] if review.find('span', {'itemprop': 'ratingValue'}) else '0'
        #     data['comment'] = review.find('span', {'itemprop': 'description'}).text if review.find(
        #         'span', {'itemprop': 'description'}) else ''

        #     data['language'] = 'en'

        #     data['establishment'] = f'/api/establishments/{self.establishment}'
        #     data['source'] = urlparse(self.url).netloc.split('.')[1]

        #     reviews.append(data)

        self.data = reviews


# trp = Hotels(url="https://uk.hotels.com/ho512192/the-standard-high-line-new-york-united-states-of-america/", establishment=33)
# trp.execute()
