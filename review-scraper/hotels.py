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


class Hotels(Scraping):

    def __init__(self, url: str, establishment: str):
        super().__init__(in_background=False, url=url, establishment=establishment)

    def close_popup(self) -> None:
        try:
            self.driver.find_element(By.CLASS_NAME, 'osano-cm-button--type_accept').click()
        except:
            pass

    def load_reviews(self) -> None:
        self.close_popup()
        button_review = self.driver.find_element(By.CSS_SELECTOR, '#Reviews > div > div > div:nth-child(2) > div > button')
        try:
            button_review.click()
            try:
                button_review.click()
            except:
                pass
            time.sleep(2)
            button_view_more = self.driver.find_element(By.CSS_SELECTOR, '#app-layer-reviews-property-reviews-1 > section > div.uitk-sheet-content.uitk-sheet-content-padded.uitk-sheet-content-extra-large > div > div.uitk-layout-grid.uitk-layout-grid-align-content-start.uitk-layout-grid-has-auto-columns.uitk-layout-grid-has-columns.uitk-layout-grid-has-space.uitk-layout-grid-display-grid.uitk-layout-grid-item.uitk-layout-grid-item-has-column-start.uitk-layout-grid-item-has-column-start-by-medium.uitk-layout-grid-item-has-column-start-by-large.uitk-layout-grid-item-has-column-start-by-extra_large > div.uitk-layout-grid-item > section > div.uitk-spacing.uitk-type-center.uitk-spacing-margin-block-three > button')
            while button_view_more.is_displayed():
                try:
                    self.driver.find_element(By.CSS_SELECTOR, '#app-layer-recommendations-overlay > section > div.uitk-layout-flex.uitk-layout-flex-align-items-center.uitk-toolbar > button').click()
                except:
                    pass
                button_view_more.click()
                WebDriverWait(self.driver, 5)
                time.sleep(1)
        except: 
            pass

    def extract(self) -> None:
        def fomat_date(date:str) -> str:
            date = date.split(' ')
            month = month_number(date[1], 'fr', 'short')
            return f'{date[0]}/{month}/{date[2]}'

        reviews = []

        self.load_reviews()

        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        review_cards = soup.find('div', {'data-stid':'property-reviews-list'}).find_all('article', {'itemprop':'review'})

        for review in review_cards:
            data = {}
            data['date_review'] = fomat_date(review.find('span', {'itemprop':'datePublished'}).text.strip())
            data['author'] = review.find('img').parent.text.split(',')[0]
            data['rating'] = review.find('span', {'itemprop':'ratingValue'}).text.split(' ')[0] if review.find('span', {'itemprop':'ratingValue'}) else '0'
            data['comment'] = review.find('span', {'itemprop':'description'}).text if review.find('span', {'itemprop':'description'}) else ''

            try:
                data['language'] = detect(data['comment']) if data['comment'] else 'fr'

            except:
                data['language'] = 'fr'
                data['comment'] = ''

            data['establishment'] = f'/api/establishments/{self.establishment}'
            data['source'] = urlparse(self.url).netloc.split('.')[1]
            
            reviews.append(data)
        
        self.data = reviews


# trp = Hotels(url="https://fr.hotels.com/ho1100722624/okko-hotels-paris-gare-de-l-est-paris-france")
# trp.execute()