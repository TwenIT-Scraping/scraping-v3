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
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from langdetect import detect
from tools import month_number


class Tripadvisor(Scraping):
    def __init__(self, url: str, establishment: str):
        super().__init__(in_background=False, url=url, establishment=establishment)

    def extract(self):
        reviews = []

        time.sleep(10)

        try:
            while True:
                page = self.driver.page_source

                soupe = BeautifulSoup(page, 'lxml')

                reviews_card = soupe.find_all('div', {'data-test-target':"HR_CC_CARD"})

                for item in reviews_card:
                    try:
                        title = item.find('div', {'data-test-target':'review-title'}).text.strip() if item.find('div', {'data-test-target':'review-title'}) else ''
                    except:
                        print("Erreur titre")

                    try:
                        detail = item.find('span', {'class':'QewHA'}).find('span').text.strip().replace('\n', '') if item.find('span', {'class':'QewHA'}) else ''
                    except:
                        print("Erreur detail")
                    
                    try:
                        comment = f"{title}{': ' if title and detail else ''}{detail}"
                    except:
                        print("Erreur comment")
                    
                    try:
                        lang = detect(comment)
                    except:
                        lang = 'en'

                    year = datetime.today().year
                    month = datetime.today().month
                    day = datetime.today().day

                    try:
                        date_raw = item.find('div', {'class': 'cRVSd'}).text.strip()
                        print(date_raw)
                        date_rawt = date_raw.split()[-2:]

                        if int(date_rawt[1]) > 2000:
                            year = date_rawt[1]
                            day = (datetime.today() + timedelta(days=-1)).day
                        else:
                            day = date_rawt[1]
                            year = datetime.today().year
                        
                        month = month_number(date_rawt[0], 'en', 'short')
                    except Exception as e:
                        print("Erreur date")
                        print(e)

                    review_data = {
                        'comment': comment,
                        'rating': str(int(item.find('span', class_='ui_bubble_rating')['class'][1].split('_')[1]) / 10) + "/5" if item.find('span', class_='ui_bubble_rating') else "0/5",
                        'language': lang,
                        'source': urlparse(self.url).netloc.split('.')[1],
                        'author': item.find('a', class_='ui_header_link').text.strip() if item.find('a', class_='ui_header_link') else "",
                        'establishment': f'/api/establishments/{self.establishment}',
                        'date_review': f"{day}/{month}/{year}"
                    }

                    reviews.append(review_data)

                try:
                    next_btn = self.driver.find_element(By.CSS_SELECTOR, "a.nav.next")
                    disable_btn = 'disabled' in next_btn.get_attribute('class').split()
                    if next_btn and not disable_btn:
                        self.driver.execute_script("arguments[0].click();", next_btn)
                        time.sleep(5)
                    else:
                        break
                    
                except Exception as e:
                    break

            self.data = reviews

        except Exception as e:
            print("erreur:", e)
        



# trp = Tripadvisor(url="https://www.tripadvisor.com/Hotel_Review-g60763-d122020-Reviews-Chelsea_Pines_Inn-New_York_City_New_York.html", establishment=33)
# trp.execute()
# print(trp.data)