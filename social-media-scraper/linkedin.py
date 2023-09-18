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


class Linkedin(Scraping):
    def __init__(self, url: str, establishment: str, site_url: str):
        super().__init__(in_background=False, url=url, establishment=establishment, site_url=site_url)

    def login(self):
        self.scrap(self.site_url)
        time.sleep(20)
        # login_form = self.driver.find_element(By.ID, "loginForm")
        # email_input = self.driver.find_element(By.NAME, "email-or-phone").send_keys("joharyandrianjafimanohisolo@gmail.com")
        # password_input = self.driver.find_element(By.NAME, "password").send_keys("jOx3rBNT5Ax9")
        # time.sleep(2)
        # login_form.find_element(By.XPATH, "//button[@type='submit']").click()
        # time.sleep(5)


        # if self.driver.find_element(By.XPATH, "//div[@role='dialog']"):
        #     


    # def load_reviews(self) -> None:
    #     self.driver.find_element(By.ID, 'avis-tout-cta').click()
    #     results = int(''.join([x for x in self.driver.find_element(By.ID, 'avis-comp-content').find_element(By.CLASS_NAME, 'ml-1').text if x.isdigit()]))
    #     for i in range(results//3):
    #         self.driver.find_element(By.ID, 'avis-cards-content-container').click()
    #         for k in range(3):
    #             self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
    #         time.sleep(2)

    def extract(self) -> None:
        try:
            pass
            # time.sleep(10)
            # soup  = BeautifulSoup(self.driver.page_source, 'lxml')
            # nb_followers = soup.find_all('a', href=lambda href: href and "/followers/" in href)[0].find('span', {'title': True})['title']
            # print(nb_followers)
                    # self.load_reviews()

        # reviews = []

        # try:
        #     soup  = BeautifulSoup(self.driver.page_source, 'lxml')
        #     followers = soup.find_all('a', href=lambda href: href and "/followers/" in href)[0].text.strip()
        #     print(followers)
        #     tab = followers.split(' ')
        #     print(tab)
        #     nb = tab[0].replace(',', ' ') + ('000' if len(tab) > 1 and tab[1] == 'K' else '')
        #     print(nb)
        #     # review_cards = soup.find('div', {'id':'avis-cards-content-container'}).find_all('div', {'typeof':'comment'})
            
        #     # for review in review_cards:
        #     #     date = review.find('span', {'property':'dateCreated'})['content']
        #     #     data = {}
        #     #     data['author'] = review.find('div', class_='date-publication').find('strong').text.strip()
        #     #     data['date_review'] = '/'.join(date.split('-')[::-1])
        #     #     data['comment'] = review.find('p', class_='avis-comment').text.strip() if review.find('p', class_='avis-comment') else ''
        #     #     data['rating'] = review.find('span', class_='score-text').text if review.find('span', class_='score-text') else 0
        #     #     data['language'] = detect(data['comment'])
        #     #     data['source'] = urlparse(self.url).netloc.split('.')[1]
        #     #     data['establishment'] = f'/api/establishments/{self.establishment}'
        #     #     reviews.append(data)

        except Exception as e:
            print('extraction file')
            print(e)

        # self.data = reviews


instance = Linkedin(url="https://www.linkedin.com/company/chateau-de-candie", establishment=2, site_url="https://www.linkedin.com/")
instance.execute()