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
from tools import month_number
from selenium.webdriver.support.select import Select


class Booking(Scraping):
    def __init__(self, url: str, establishment: str):
        super().__init__(in_background=False, url=url, establishment=establishment)

    def extract(self):

        reviews = []

        review_order = Select(self.driver.find_element(
            By.XPATH, "//select[@id='sorting']"))
        review_order.select_by_value('completed_desc')

        self.driver.find_element(
            By.XPATH, "//div[@class='review_list_nav_wrapper clearfix']/form/input[@type='submit']").click()

        while True:
            time.sleep(10)

            page = self.driver.page_source

            soupe = BeautifulSoup(page, 'lxml')

            review_cards = soupe.find_all('li', {'itemprop': 'review'})

            for card in review_cards:
                title = card.find('div', {'class': 'review_item_header_content'}).text.strip(
                ) if card.find('div', {'class': 'review_item_header_content'}) else ""
                negative = card.find('p', {'class': 'review_neg'}).text.strip(
                ) if card.find('p', {'class': 'review_neg'}) else ""
                positive = card.find('p', {'class': 'review_pos'}).text.strip(
                ) if card.find('p', {'class': 'review_pos'}) else ""
                detail = f'{positive} | {negative}' if positive and negative else (
                    positive if positive else negative)
                comment = f"{title}{': ' if title and detail else ''}{detail}"

                raw_date = card.find('p', {'class': 'review_item_date'}).text.strip(
                ) if card.find('p', {'class': 'review_item_date'}) else ""
                dates = raw_date.split()
                try:
                    date_review = f"{dates[-3]}/{month_number(dates[-2], 'fr')}/{dates[-1]}"
                except Exception as e:
                    date_review = f"{dates[-3]}/{month_number(dates[-2], 'en')}/{dates[-1]}"

                try:
                    lang = detect(comment)
                except:
                    lang = 'en'

                try:
                    reviews.append({
                        'comment': comment,
                        'rating': card.find('span', {'class': 'review-score-badge'}).text.strip()
                        if card.find('span', {'class': 'review-score-badge'}) else "0",
                        'date_review': date_review,
                        'language': lang,
                        'source': urlparse(self.url).netloc.split('.')[1],
                        'author': card.find('p', {'class': 'reviewer_name'}).text.strip() if card.find('p', {'class': 'reviewer_name'}) else "",
                        'establishment': f'/api/establishments/{self.establishment}'
                    })
                except Exception as e:
                    print(e)
                    continue

            if not self.check_date(reviews[-1]['date_review']):
                break

            try:

                next_btn = self.driver.find_element(
                    By.ID, 'review_next_page_link')

                if next_btn:
                    self.driver.execute_script(
                        "arguments[0].click();", next_btn)
                    time.sleep(4)

            except Exception as e:
                break

        self.data = reviews


# trp = Booking(url="https://www.booking.com/reviews/fr/hotel/la-belle-etoile-les-deux-alpes.fr.html")
# trp.execute()
# print(trp.data)
