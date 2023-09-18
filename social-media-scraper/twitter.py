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


class Twitter(Scraping):
    def __init__(self, url: str, establishment: str, site_url: str):
        super().__init__(in_background=False, url=url, establishment=establishment, site_url=site_url)

    def login(self):
        self.scrap(self.site_url)
        time.sleep(10)
        # login_form = self.driver.find_element(By.XPATH, "//form[@data-testid='royal_login_form']")
        self.driver.find_element(By.XPATH, "//input[@autocomplete='username']").send_keys("joharyandrianjafimanohisolo@gmail.com")
        time.sleep(5)
        self.driver.find_elements(By.XPATH, "//div[@role='button']")[2].click()
        time.sleep(10)
        self.driver.find_element(By.XPATH, "//div[@data-testid='ocfEnterTextTextInput']").send_keys("joharyandrianjafimanohisolo@gmail.com")
        time.sleep(5)
        self.driver.find_element(By.XPATH, "//button[@data-testid='ocfEnterTextNextButton']").click()
        
        # password_input = self.driver.find_element(By.XPATH, "//input[@autocomplete='current-password']").send_keys("sdq3$e5eA1@&0")
        # time.sleep(15)
        # login_btn = self.driver.find_element(By.XPATH, "//div[@data-testid='LoginForm_Login_Button']").click()
        # time.sleep(10)
        # login_form.find_element(By.XPATH, "//button[@data-testid='royal_login_button']").click()


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
            pass
            # time.sleep(10)
            # soup  = BeautifulSoup(self.driver.page_source, 'lxml')
            # followers = soup.find_all('a', href=lambda href: href and "followers" in href)[0].text.strip()
            # nb_followers = format_number(followers)
            
            # print(nb_followers)
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


instance = Twitter(url="https://twitter.com/ChateaudeCandie", establishment=2, site_url="https://twitter.com/i/flow/login")
instance.execute()