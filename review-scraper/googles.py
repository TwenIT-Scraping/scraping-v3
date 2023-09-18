import random
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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class Google(Scraping):
    def __init__(self, url: str, establishment: str):
        super().__init__(in_background=False, url=url, establishment=establishment)

    def load_reviews(self):
        results = int(''.join([x for x in self.driver.find_element(By.CSS_SELECTOR, '#reviews > c-wiz > c-wiz > div > div > div > div > div.ChBWlb.TjtFVc > div.pDLIp > div > div.zhMoVd.nNUNpc > div.UkIqCb > div > span').text if x.isdigit()]))
        for i in range(results//6):
            for k in range(5):
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(3)
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)

    def extract(self):
        def formate_date(raw_date):
            split_date = date_raw.split()
            today = datetime.now()
                
            if split_date[4] == 'jour':
                return datetime.strftime(today + timedelta(days=-1), '%d/%m/%Y')
            elif split_date[4] == 'jours':
                return datetime.strftime(today + timedelta(days=-(int(split_date[3]))), '%d/%m/%Y')
            if split_date[4] == 'semaine':
                return datetime.strftime(today + timedelta(days=-7), '%d/%m/%Y')
            elif split_date[4] == 'semaines':
                return datetime.strftime(today + timedelta(days=-7*int(split_date[3])), '%d/%m/%Y')
            elif split_date[4] == 'mois':
                if split_date[3] == 'un':
                    return datetime.strftime(today + timedelta(days=-31), '%d/%m/%Y')
                else:
                    return datetime.strftime(today + timedelta(days=-31*int(split_date[3])), '%d/%m/%Y')
            elif split_date[4] == 'an':
                return datetime.strftime(today + timedelta(days=-365), '%d/%m/%Y')
            elif split_date[4] == 'ans':
                return datetime.strftime(today + timedelta(days=-(int(split_date[3])*365)), '%d/%m/%Y')
            else:
                return datetime.strftime(today, '%d/%m/%Y')
            
        time.sleep(3)

        try:
            accept_btn = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Tout accepter')]")
            self.driver.execute_script("arguments[0].click();", accept_btn)
            time.sleep(random.randint(2, 5))
        except:
            pass

        time.sleep(5)

        self.load_reviews()

        reviews = []

        page = self.driver.page_source

        soupe = BeautifulSoup(page, 'lxml')

        review_container = soupe.find_all('div', {'jsname': "Pa5DKe"})

        for container in review_container:
            cards = container.find_all('div', {'data-hveid': True})
            for card in cards:
                author = card.find('span', {'class': 'k5TI0'}).find('a').text.strip() if card.find('span', {'class': 'k5TI0'}) and card.find('span', {'class': 'k5TI0'}).find('a') else ""
                comment = card.find('div', {'class': 'K7oBsc'}).text.strip().replace(" En savoir plus", "") if card.find('div', {'class': 'K7oBsc'}) else ""
                rating = card.find('div', {'class': 'GDWaad'}).text.strip().split('/')[0] if card.find('div', {'class': 'GDWaad'}) else "0"

                try:
                    lang = detect(comment)
                except: 
                    lang = 'en'

                date_raw = card.find('span', {'class': 'iUtr1'}).text.strip() if card.find('span', {'class': 'iUtr1'}) else ""
                
                date_review = formate_date(date_raw) if date_raw else "01/01/2022"

                if author or comment or rating != "0":

                    reviews.append({
                        'rating': rating,
                        'author': author,
                        'date_review': date_review,
                        'comment': comment,
                        'language': lang,
                        'source': urlparse(self.url).netloc.split('.')[1],
                        'establishment': f'/api/establishments/{self.establishment}'
                    })

        self.data = reviews


# trp = Google(url="https://www.google.fr/travel/search?q=les%20balcons%20d%27aix&g2lb=2502548%2C2503771%2C2503781%2C4258168%2C4270442%2C4284970%2C4291517%2C4306835%2C4597339%2C4754388%2C4757164%2C4814050%2C4850738%2C4864715%2C4874190%2C4886480%2C4893075%2C4924070%2C4965990%2C4985712%2C4990494%2C72248281%2C72254381%2C72271797%2C72276651%2C72279098%2C72281254&hl=fr-FR&gl=fr&ssta=1&ts=CAESABpJCikSJzIlMHg0NzhiYTQyNmFjZTRmY2VmOjB4YjI1OTUyNmUzODQ2NTdhMxIcEhQKBwjnDxAGGBsSBwjnDxAGGBwYATIECAAQACoHCgU6A01HQQ&qs=CAEyJkNoZ0lvNi1ad3VQTjFLeXlBUm9MTDJjdk1YUjNYMjB6Y1hFUUFROAJCCwmjV0Y4blJZshgBQgsJo1dGOG5SWbIYAQ&ap=ugEHcmV2aWV3cw&ictx=1&sa=X")
# trp.execute()
# print(trp.data)