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
from tools import shortmonths_fr,months_es, months_fr, months_es
from random import randint
from selenium.webdriver.support.select import Select
import locale
from langdetect import detect


class BaseHotelsReviewScrap(Scraping):
    def __init__(self, url: str, establishment: str, settings: str, env: str, last_review_date):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, settings=settings, env=env, last_review_date=last_review_date)
        
    def goto_page(self) -> None:
        print(f"url: {self.url}")
        self.driver.get(self.url)
        time.sleep(10)
        #input('check the driver for debugging')
        try:
            self.driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()
            WebDriverWait(self.driver, 10000)
            self.first_pop_up_closed = True
            print('cookies closed')
            time.sleep(5) #on attend le rechargement car il y en a si il y avait ce popup
        except:
            time.sleep(1)

    def scroll_down_page(self):
        #print("scroll down page")
        print("Clique sur bouton reviews")
        """commenté le 08 10 2024
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
                #self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
                time.sleep(1)"""
        time.sleep(10)
        self.driver.find_element(By.CSS_SELECTOR, "button[data-stid='reviews-link']").click()
        time.sleep(2)

    def close_popup(self):
        try:
            self.driver.find_element(By.CSS_SELECTOR, "#app-layer-recommendations-overlay > section > div.uitk-layout-flex.uitk-layout-flex-align-items-center.uitk-toolbar > button").click()
            WebDriverWait(self.driver, 10000)
            self.second_pop_up_closed = True
            print('suggestion popup closed')
        except:
            time.sleep(2)

    def get_last_date(self) -> object:
        page = self.driver.page_source
        soupe = BeautifulSoup(page, 'lxml')
        last_review_cards = soupe.find('div', {'class', 'uitk-card uitk-card-roundcorner-all uitk-card-has-primary-theme'}).find_all('article', {'itemprop':'review'})[-1]
        last_date = last_review_cards.find('span', {'itemprop': 'datePublished'}).text.strip() if last_review_cards.find('span', {'itemprop': 'datePublished'}) else ""
        #last_date = self.format_date(reviews[-1].find('span', {'itemprop':'datePublished'}).text.strip())
        print(f'last date' + last_date)

        #Traitement des dates
        if 'hotels.com/es/' in self.driver.current_url:
            date_split = last_date.split(' ') #on a ici 0 à 4 dans date split car il y a les "de"
            day = date_split[0]
            month = months_es[date_split[2]]
            year = date_split[4]
            date_review = datetime.strptime(f'{day}/{month}/{year}', '%d/%m/%Y')
            return date_review
        else:
            try:
                date_split = last_date.split(' ')
                day = date_split[0]
                if '.' in date_split[1]:
                    month = shortmonths_fr[date_split[1]]
                else:
                    month = shortmonths_fr[date_split[1]]
                year = date_split[2]
                print(f'{day}/{month}/{year}')
                return datetime.strptime(f'{day}/{month}/{year}', '%d/%m/%Y')
            except:
                """ comment é le 08 10 2024
                date_rawt = last_date.split()
                date_review = "%s/%s/%s" % (date_rawt[0], month_number(
                    date_rawt[1], 'fr', 'short'), date_rawt[2])"""
                print('Hotels.com FR , erreur au niveau du formattage de la date dans la classe BaseHotelsReviewScrap() méthode get_last_date()')

            

        
        
    def count_review(self):
        print(" Count review")
        review_container = BeautifulSoup(self.driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/section/div[3]/div/div[2]/div[4]/section/div[1]/div').get_attribute('innerHTML'), 'lxml')
        reviews = review_container.find_all('article', {'itemprop':'review'})
        print(f'reviews {len(reviews)} loaded')

    def load_review(self):
        print("loading reviews")
        time.sleep(6)
        self.close_popup()
        self.driver.find_element(By.XPATH, "//option[@value='NEWEST_TO_OLDEST']").click()

        time.sleep(5)
        """ commenté le 08 10 2024
        review_container = BeautifulSoup(self.driver.find_element(By.ID, 'Reviews').get_attribute('innerHTML'), 'lxml')
        btn_view = review_container.find('button', {'class':'uitk-button uitk-button-medium uitk-button-has-text uitk-button-secondary'})
        self.btn_text = btn_view.text.strip()"""
        self.last_date = self.get_last_date()
        # Encore tsy hitako izay ilavana azy -> if btn_view:
        self.scroll_element()
        # Encore un -> btn_view_more = self.driver.find_element(By.XPATH, f"//button[contains(text(), '{btn_view.text.strip()}')]")
        # print('btn cliqued')
        """ suite de condition commenté le 08 10 2024 -> and btn_view_more.is_displayed()"""
        #while self.last_date > (datetime.now() - timedelta(days=365)):
        while self.last_date > (datetime.now() - timedelta(days=365)):
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
        review_container = BeautifulSoup(self.driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/section/div[3]/div/div[2]/div[4]/section/div[1]/div').get_attribute('innerHTML'), 'lxml')
        #nocommenteko 07 10 2024 reviews_cards = review_container.find_all('article', {'itemprop':'review'})

        try:
            
            reviews_cards = review_container.find_all('article', {'itemprop':'review'})
            
        except Exception as e:
            print(f'ERREUR dans extract() de la classe BaseHotelsReviewScrap() ==> {e}')

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
                date_review = self.format_date(card.find('span', {'itemprop': 'datePublished'}).text.strip())
                data = {}
                data['date_review'] = date_review
                data['author'] = card.find('img').parent.text.split(',')[0]
                data['rating'] = card.find('span', {'itemprop': 'ratingValue'}).text.split(
                    ' ')[0] if card.find('span', {'itemprop': 'ratingValue'}) else '0'
                data['comment'] = card.find('span', {'itemprop': 'description'}).text if card.find('span', {'itemprop': 'description'}) else ''

                data['language'] = lang

                data['establishment'] = f'/api/establishments/{self.establishment}'
                data['settings'] = f'/api/establishments/{self.settings}'
                data['source'] = urlparse(self.driver.current_url).netloc.split('.')[1]
                data['source'] = 'hotels'
                data['date_visit'] = date_review
                data['novisitday'] = "0"
                
                if datetime.strptime(date_review, '%d/%m/%Y') > datetime.now() - timedelta(days=365) or (datetime.strptime(date_review, '%d/%m/%Y') > (datetime.strptime(self.last_review_date, '%d/%m/%Y') + timedelta(days=1))):
                #if datetime.strptime(data['date_review'], "%d/%m/%Y") > (datetime.now() - timedelta(days=365)):
                    reviews.append(data)
            except Exception as e:
                print(e)
                pass
        print(f'Self.data => {reviews}')
        self.data = reviews
        self.driver.close()

        """ Save """
        self.save()


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
        self.lang = 'fr'
    def format_date(self, date:str) -> str:
        date = date.split(' ')
        return f"{date[0]}/{shortmonths_fr[date[1]]}/{date[2]}"
    

class Hotels_EN(BaseHotelsReviewScrap):

    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(url, establishment, settings, env)
        self.lang = 'en' 

    def format_date(self, date:str) -> str:
        date = date.split(' ')
        return f"{date[0]}/{shortmonths_fr[date[1]]}/{date[2]}"

class Hotels_ES(BaseHotelsReviewScrap):

    def __init__(self, url: str, establishment: str, settings: str, env: str):
        super().__init__(url, establishment, settings, env)
        self.lang = 'es' 

    def format_date(self, date:str) -> str:
        date = date.split(' ')
        return f"{date[0]}/{months_es[date[2]]}/{date[4]}" #4 car il y a les 'de'





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


