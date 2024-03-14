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
from models import Settings
from requests.models import PreparedRequest


class Booking(Scraping):
    def __init__(self, url: str, establishment: str, settings: str, env: str):
        defurl = url if url.endswith('.fr.html') else f"{url}.fr.html"
        super().__init__(in_background=False, url=defurl,
                         establishment=establishment, settings=settings, env=env)

    def set_language(self, language) -> None:
        super().set_language(language)
        url = self.url.split('?')[0]
        params = {'r_lang': self.lang, 'order': 'completed_desc'}
        req = PreparedRequest()
        req.prepare_url(url, params)
        super().set_url(req.url)

    def check_page(self) -> None:
        try:
            page_404 = self.driver.find_element(
                By.XPATH, "//div[@id='error404page']")
            Settings.disable_setting(self.setting_id, env=self.env)
            return False if page_404 else True
        except:
            return True

    def extract(self):

        reviews = []

        # review_order = Select(self.driver.find_element(
        #     By.XPATH, "//select[@id='sorting']"))
        # review_order.select_by_value('completed_desc')

        try:
            # view_list_btn = self.driver.find_element(
            #     By.XPATH, "//div[@class='review_list_nav_wrapper clearfix']/form/input[@type='submit']")
            # self.driver.execute_script("arguments[0].click();", view_list_btn)

            while True:
                time.sleep(5)

                page = self.driver.page_source

                soupe = BeautifulSoup(page, 'lxml')

                review_cards = soupe.find_all('li', {'itemprop': 'review'})
                count = len(review_cards)

                print(f"====> {count} cards trouvés !")

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
                    if card.find('p', {'class': 'review_staydate '}):
                        date_visit_raw = card.find(
                            'p', {'class': 'review_staydate '}).text.strip().split()[-2:]
                        date_visit = f"{(datetime().day-1)}/{month_number(date_visit_raw[0], 'en')}/{date_visit_raw[1]}"
                        print(date_visit)
                    else:
                        date_visit = date_review

                    try:
                        lang = detect(comment)
                    except:
                        lang = 'en'

                    print(self.lang, lang)

                    try:
                        if self.lang and lang == self.lang:
                            reviews.append({
                                'comment': comment,
                                'rating': card.find('span', {'class': 'review-score-badge'}).text.strip()
                                if card.find('span', {'class': 'review-score-badge'}) else "0",
                                'date_review': date_review,
                                'language': lang,
                                'source': urlparse(self.url).netloc.split('.')[1],
                                'author': card.find('p', {'class': 'reviewer_name'}).text.strip() if card.find('p', {'class': 'reviewer_name'}) else "",
                                'establishment': f'/api/establishments/{self.establishment}',
                                'settings': f'/api/settings/{self.settings}',
                                'date_visit': date_review,
                                'novisitday': "0"
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

        except:
            pass

        self.data = reviews


class Booking_ES(Booking):
    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(url=url, establishment=establishment, settings=settings, env=env)
        # self.lang = "es"


# trp = Booking(url="https://www.booking.com/reviews/fr/hotel/la-belle-etoile-les-deux-alpes.fr.html")
# trp.execute()
# print(trp.data)
