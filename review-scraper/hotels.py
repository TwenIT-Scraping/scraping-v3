import random
from scraping import Scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from abc import abstractmethod
import sys
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from langdetect import detect
from tools import shortmonths_fr,months_es, shortmonths_en
from random import randint
from selenium.webdriver.support.select import Select
import locale
from langdetect import detect


class BaseHotelsReviewScrap(Scraping):
    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, settings=settings, env=env)
        
    def goto_page(self) -> None:
        print(f"url: {self.url}")
        self.driver.get(self.url)
        WebDriverWait(self.driver, 10000)
        time.sleep(randint(30, 60))
        try:
            self.driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()
            WebDriverWait(self.driver, 10000)
            self.first_pop_up_closed = True
            print('cookies closed')
        except:
            time.sleep(1)

    def scroll_down_page(self):
        print("scroll down page")
        while True:
            try:
                review_container = BeautifulSoup(self.driver.find_element(By.ID, 'Reviews').get_attribute('innerHTML'), 'lxml')
                btn_view = review_container.find('button', {'class':'uitk-button uitk-button-medium uitk-button-has-text uitk-button-secondary'})
                if btn_view:
                    btn = self.driver.find_element(By.XPATH, f"//button[contains(text(), '{btn_view.text.strip()}')]")
                    btn.click()
                    time.sleep(3)
                    break
            except NoSuchElementException:
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
                time.sleep(1)

    def close_popup(self):
        try:
            self.driver.find_element(By.CSS_SELECTOR, "#app-layer-recommendations-overlay > section > div.uitk-layout-flex.uitk-layout-flex-align-items-center.uitk-toolbar > button").click()
            WebDriverWait(self.driver, 10000)
            self.second_pop_up_closed = True
            print('suggestion popup closed')
        except:
            time.sleep(2)

    def get_last_date(self) -> object:
        review_container = BeautifulSoup(self.driver.find_element(By.CSS_SELECTOR, '#app-layer-reviews-property-reviews-1 > section > div.uitk-sheet-content.uitk-sheet-content-padded.uitk-sheet-content-extra-large > div > div.uitk-layout-grid.uitk-layout-grid-has-auto-columns.uitk-layout-grid-has-columns.uitk-layout-grid-has-columns-by-medium.uitk-layout-grid-has-columns-by-large.uitk-layout-grid-display-grid > div.uitk-layout-grid-item.uitk-spacing.uitk-spacing-margin-blockstart-six > section > div:nth-child(1) > div').get_attribute('innerHTML'), 'lxml')
        reviews = review_container.find_all('article', {'itemprop':'review'})
        last_date = self.format_date(reviews[-1].find('span', {'itemprop':'datePublished'}).text)
        print(f'last date' + last_date)
        return datetime.strptime(last_date, '%d/%m/%Y')
        
    def count_review(self):
        print(" extracting data")
        review_container = BeautifulSoup(self.driver.find_element(By.ID, 'app-layer-reviews-property-reviews-1').get_attribute('innerHTML'), 'lxml')
        reviews = review_container.find_all('article', {'itemprop':'review'})
        print(f'reviews {len(reviews)} loaded')

    def load_review(self):
        print("loading reviews")
        time.sleep(6)
        self.close_popup()
        self.driver.find_element(By.XPATH, "//option[@value='NEWEST_TO_OLDEST']").click()
        time.sleep(5)
        review_container = BeautifulSoup(self.driver.find_element(By.ID, 'Reviews').get_attribute('innerHTML'), 'lxml')
        btn_view = review_container.find('button', {'class':'uitk-button uitk-button-medium uitk-button-has-text uitk-button-secondary'})
        self.btn_text = btn_view.text.strip()
        self.last_date = self.get_last_date()
        if btn_view:
            self.scroll_element()
            btn_view_more = self.driver.find_element(By.XPATH, f"//button[contains(text(), '{btn_view.text.strip()}')]")
            # print('btn cliqued')
            while self.last_date > (datetime.now() - timedelta(days=365)) and btn_view_more.is_displayed():
                self.close_popup()
                self.count_review()
                self.scroll_element()
                time.sleep(2)
                self.last_date = self.get_last_date()

    def scroll_element(self):
            print("scrolling element")
            try:
                btn_view_more_container = BeautifulSoup(self.driver.find_element(By.XPATH, '//div[@data-stid="property-reviews-list"]').get_attribute('innerHTML'), 'lxml')
                btn_view_more_text = btn_view_more_container.find('button', {'class':'uitk-button uitk-button-medium uitk-button-has-text uitk-button-secondary'})
                btn_view_more = self.driver.find_element(By.XPATH, f'//button[contains(text(), "{btn_view_more_text.text.strip()}")]')
                btn_view_more.location_once_scrolled_into_view
                time.sleep(random.randint(1, 2))
                btn_view_more.click()
            except:
                print('btn not found')

    def extract(self):
        print(" extracting data")
        reviews = []
        review_container = BeautifulSoup(self.driver.find_element(By.ID, 'app-layer-reviews-property-reviews-1').get_attribute('innerHTML'), 'lxml')
        reviews_cards = review_container.find_all('article', {'itemprop':'review'})
        for card in reviews_cards:
            try:
                comment = card.find('span', {'itemprop': 'description'}).text
            except:
                comment = ''
                pass

            lang = self.lang

            try:
                lang = detect(comment)
            except Exception as e:
                pass

            try:
                data = {}
                data['date_review'] = self.format_date(card.find(
                    'span', {'itemprop': 'datePublished'}).text.strip())
                data['author'] = card.find('img').parent.text.split(',')[0]
                data['rating'] = card.find('span', {'itemprop': 'ratingValue'}).text.split(
                    ' ')[0] if card.find('span', {'itemprop': 'ratingValue'}) else '0'
                data['comment'] = card.find('span', {'itemprop': 'description'}).text if card.find('span', {'itemprop': 'description'}) else ''

                data['language'] = lang

                data['establishment'] = f'/api/establishments/{self.establishment}'
                data['settings'] = f'/api/establishments/{self.settings}'
                data['source'] = urlparse(self.driver.current_url).netloc.split('.')[1]
                data['source'] = 'hotels'
                data['date_visit'] = data['date_review']
                data['novisitday'] = "0"
                if datetime.strptime(data['date_review'], "%d/%m/%Y") > (datetime.now() - timedelta(days=365)):
                    reviews.append(data)
                print(data)
            except Exception as e:
                print(e)
                pass
        
        self.data = reviews


    def execute(self) -> None:
        self.goto_page()
        self.scroll_down_page()
        self.close_popup()
        self.load_review()
        self.extract()

    @abstractmethod
    def format_date(self, date:str) -> str:
            pass
    
class Hotels_FR(BaseHotelsReviewScrap):

    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(url, establishment, settings, env)

    def format_date(self, date:str) -> str:
        date = date.split(' ')
        return f"{date[0]}/{shortmonths_fr[date[1]]}/{date[2]}"
    

class Hotels_EN(BaseHotelsReviewScrap):

    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(url, establishment, settings, env)
        self.lang = 'fr' 

    def format_date(self, date:str) -> str:
        date = date.split(' ')
        return f"{date[0]}/{shortmonths_fr[date[1]]}/{date[2]}"

class Hotels_ES(BaseHotelsReviewScrap):

    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(url, establishment, settings, env)
        self.lang = 'en' 

    def format_date(self, date:str) -> str:
        date = date.split(' ')
        return f"{date[0]}/{months_es[date[1]]}/{date[2]}"
        self.lang = 'es' 




class Hotels(Scraping):

    def __init__(self, url: str, establishment: str, settings: str, env: str):
        url = url + '?pwaDialog=reviews-property-reviews-1'
        super().__init__(in_background=False, url=url,
                         establishment=establishment, settings=settings, env=env)

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


class Hotels_FR_OLD(Hotels):

    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(url=url, establishment=establishment, settings=settings, env=env)

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
            # self.driver.find_element(
            #     By.XPATH, "//select[@id='sortBy']/option[@value='NEWEST_TO_OLDEST']").click()

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

        input("Veullez entrer une touche ...")

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


class Hotels_EN_OLD(Hotels):

    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(url=url, establishment=establishment, settings=settings, env=env)

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


class Hotels_ES_OLD(Hotels):

    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(url=url, establishment=establishment, settings=settings, env=env)
        locale.setlocale(locale.LC_ALL, 'es_ES.utf8')

    def format_date(self, date: str) -> str:

        date = datetime.strptime(date, '%d de %B de %Y')

        return date.strftime('%d/%m/%Y')

        # date = date.split(' ')
        # month = month_number(date[1], 'fr', 'short')

        # return f'{date[0]}/{month}/{date[2]}'

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
                By.XPATH, "//button[contains(text(), 'Ver todas las opiniones')]").click()
        except Exception as e:
            print(e)

        time.sleep(3)

        try:
            # self.driver.find_element(
            #     By.XPATH, "//select[@id='sortBy']/option[@value='NEWEST_TO_OLDEST']").click()

            time.sleep(2)

            more_btn = self.driver.find_element(
                By.XPATH, '//button[contains(text(), "Más opiniones")]')

            while more_btn.is_displayed():
                # if not self.check_date(get_last_review_date()):
                #     break

                more_btn.click()
                WebDriverWait(self.driver, 5)
                time.sleep(1)
        except:
            pass

    def extract(self) -> None:

        reviews = []

        input("Veullez entrer une touche ...")

        time.sleep(1)

        self.load_reviews()

        time.sleep(random.uniform(.5, 4.0))

        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        review_cards = soup.find('div', {
                                 'data-stid': 'property-reviews-list'}).find_all('article', {'itemprop': 'review'})

        for review in review_cards:

            comment = review.find('span', {'itemprop': 'description'}).text if review.find(
                'span', {'itemprop': 'description'}) else ''

            lang = 'es'

            try:
                lang = detect(comment)
            except Exception as e:
                pass

            # if lang == 'es':
            data = {}
            data['date_review'] = self.format_date(review.find(
                'span', {'itemprop': 'datePublished'}).text.strip())
            data['author'] = review.find('img').parent.text.split(',')[0]
            data['rating'] = review.find('span', {'itemprop': 'ratingValue'}).text.split(
                ' ')[0] if review.find('span', {'itemprop': 'ratingValue'}) else '0'
            data['comment'] = review.find('span', {'itemprop': 'description'}).text if review.find(
                'span', {'itemprop': 'description'}) else ''

            data['language'] = lang

            data['establishment'] = f'/api/establishments/{self.establishment}'
            data['settings'] = f'/api/establishments/{self.settings}'
            data['source'] = urlparse(self.url).netloc.split('.')[1]
            # data['source'] = 'hotels'
            data['date_visit'] = data['date_review']
            data['novisitday'] = "0"

            reviews.append(data)
            print(data)

        self.data = reviews


# trp = Hotels_FR(url="https://fr.hotels.com/ho1568252032/hotel-dolce-notte-saint-florent-france/", establishment=33, settings=1, env='DEV')
# trp.execute()

