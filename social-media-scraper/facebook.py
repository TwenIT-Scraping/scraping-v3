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
import re


class Facebook(Scraping):
    def __init__(self, url: str, establishment: str, site_url: str):
        super().__init__(in_background=False, url=url, establishment=establishment, site_url=site_url)

    def login(self):
        self.scrap(self.site_url)
        time.sleep(10)
        login_form = self.driver.find_element(By.XPATH, "//form[@data-testid='royal_login_form']")
        email_input = login_form.find_element(By.XPATH, "//input[@data-testid='royal_email']").send_keys("0340851090")
        password_input = login_form.find_element(By.XPATH, "//input[@data-testid='royal_pass']").send_keys("p$Rlo6&3")
        time.sleep(5)
        login_form.find_element(By.XPATH, "//button[@data-testid='royal_login_button']").click()


    # def load_reviews(self) -> None:
    #     self.driver.find_element(By.ID, 'avis-tout-cta').click()
    #     results = int(''.join([x for x in self.driver.find_element(By.ID, 'avis-comp-content').find_element(By.CLASS_NAME, 'ml-1').text if x.isdigit()]))
    #     for i in range(results//3):
    #         self.driver.find_element(By.ID, 'avis-cards-content-container').click()
    #         for k in range(3):
    #             self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
    #         time.sleep(2)

    def extract(self) -> None:
        def format_number(number):
            nb = number.split()
            if len(nb) == 3:
                if ',' in nb[0] and nb[1] == 'K':
                    return nb[0].replace(',', '') + '00'
                elif nb[1] == 'K':
                    return nb[0] + '000'
            else:
                return nb[0]

        # self.load_reviews()

        # reviews = []

        try:
            for i in range(5):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)
                
            soup  = BeautifulSoup(self.driver.page_source, 'lxml')
            likes = soup.find_all('a', href=lambda href: href and "friends_likes" in href)[0].text.strip()
            followers = soup.find_all('a', href=lambda href: href and "followers" in href)[0].text.strip()
            nb_followers = format_number(followers)
            nb_likes = format_number(likes)
            
            print(nb_likes, nb_followers)

            posts = []

            for i in range(1, 30):
                try:
                    post_item = soup.find('div', {'aria-posinset': str(i)})
                except Exception as e:
                    print("Erreur 1")
                    continue

                try:
                    title = post_item.find('h2').text.strip() if post_item.find('h2') else ""
                except:
                    print("Erreur 2")
                    pass

                likes = 0
                shares = 0
                datas = post_item.find('div', {'data-visualcompletion': 'ignore-dynamic'}).find_all('div', {'role': 'button'}) \
                        if post_item.find('div', {'data-visualcompletion': 'ignore-dynamic'}) else []
                
                for item in datas:
                    tmp = item.text.strip()
                    if "Toutes les réactions" in tmp:
                        likes = int(tmp.split()[-1])

                datas = post_item.find('div', {'data-visualcompletion': 'ignore-dynamic'}).find_all('span', {'class': ['x193iq5w', 'xeuugli', 'x13faqbe', 'x1vvkbs', 'x1xmvt09', 'x1lliihq', 'x1s928wv', 'xhkezso', 'x1gmr53x', 'x1cpjm7i', 'x1fgarty', 'x1943h6x', 'xudqn12', 'x3x7a5m', 'x6prxxf', 'xvq8zen', 'xo1l8bm', 'xi81zsa']}) \
                        if post_item.find('div', {'data-visualcompletion': 'ignore-dynamic'}) else []

                print("=================")

                values = []
                for item in datas:
                    tmp = item.text.strip()
                    if tmp.isnumeric():
                        values.append(int(tmp))

                        icon = item.parent.parent

                        print(icon)
                

                print(title, ': ', likes, ' / ', shares)


            # review_cards = soup.find('div', {'id':'avis-cards-content-container'}).find_all('div', {'typeof':'comment'})
            
            # for review in review_cards:
            #     date = review.find('span', {'property':'dateCreated'})['content']
            #     data = {}
            #     data['author'] = review.find('div', class_='date-publication').find('strong').text.strip()
            #     data['date_review'] = '/'.join(date.split('-')[::-1])
            #     data['comment'] = review.find('p', class_='avis-comment').text.strip() if review.find('p', class_='avis-comment') else ''
            #     data['rating'] = review.find('span', class_='score-text').text if review.find('span', class_='score-text') else 0
            #     data['language'] = detect(data['comment'])
            #     data['source'] = urlparse(self.url).netloc.split('.')[1]
            #     data['establishment'] = f'/api/establishments/{self.establishment}'
            #     reviews.append(data)

        except Exception as e:
            print('extraction file')
            print(e)

        # self.data = reviews


instance = Facebook(url="https://www.facebook.com/chateaucandie/?locale=fr_FR", establishment=2, site_url="https://www.facebook.com")
instance.execute()