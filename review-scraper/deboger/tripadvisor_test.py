from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from unidecode import unidecode
from pathlib import Path
from datetime import datetime, timedelta
from lingua import Language, LanguageDetectorBuilder
from bs4 import BeautifulSoup
import json
import time
import random

import json
import os
from playwright.sync_api import sync_playwright
from nested_lookup import nested_lookup
from datetime import datetime, timedelta
import time
import re

import asyncio
import json
import math
from typing import List, Dict, Optional
from httpx import AsyncClient, Response
from parsel import Selector

client = AsyncClient(
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9",
    },
    follow_redirects=True
)

def parse_hotel_page(result: Response) -> Dict:
    """parse hotel data from hotel pages"""
    selector = Selector(result.text)
    basic_data = json.loads(selector.xpath("//script[contains(text(),'aggregateRating')]/text()").get())
    description = selector.css("div.fIrGe._T::text").get()
    amenities = []
    for feature in selector.xpath("//div[contains(@data-test-target, 'amenity')]/text()"):
        amenities.append(feature.get())
    reviews = []
    for review in selector.xpath("//div[@data-reviewid]"):
        title = review.xpath(".//div[@data-test-target='review-title']/a/span/span/text()").get()
        text = review.xpath(".//span[@data-test-target='review-text']/span/text()").get()
        rate = review.xpath(".//div[@data-test-target='review-rating']/span/@class").get()
        rate = (int(rate.split("ui_bubble_rating")[-1].split("_")[-1].replace("0", ""))) if rate else None
        trip_data = review.xpath(".//span[span[contains(text(),'Date of stay')]]/text()").get()
        reviews.append({
            "title": title,
            "text": text,
            "rate": rate,
            "tripDate": trip_data
        })

    return {
        "basic_data": basic_data,
        "description": description,
        "featues": amenities,
        "reviews": reviews
    }


async def scrape_hotel(url: str, max_review_pages: Optional[int] = None) -> Dict:
    """Scrape hotel data and reviews"""
    first_page = await client.get(url)
    assert first_page.status_code == 403, "request is blocked"
    hotel_data = parse_hotel_page(first_page)

    # get the number of total review pages
    _review_page_size = 10
    total_reviews = int(hotel_data["basic_data"]["aggregateRating"]["reviewCount"])
    total_review_pages = math.ceil(total_reviews / _review_page_size)

    # get the number of review pages to scrape
    if max_review_pages and max_review_pages < total_review_pages:
        total_review_pages = max_review_pages
    
    # scrape all review pages concurrently
    review_urls = [
        # note: "or" stands for "offset reviews"
        url.replace("-Reviews-", f"-Reviews-or{_review_page_size * i}-")
        for i in range(1, total_review_pages)
    ]
    for response in asyncio.as_completed(review_urls):
        data = parse_hotel_page(await response)    
        hotel_data["reviews"].extend(data["reviews"])
    print(f"scraped one hotel data with {len(hotel_data['reviews'])} reviews")
    return hotel_data

async def run():
    hotel_data = await scrape_hotel(
        url="https://www.tripadvisor.com/Hotel_Review-g190327-d264936-Reviews-1926_Hotel_Spa-Sliema_Island_of_Malta.html"    ,
        max_review_pages=3,    
    )
    # print the result in JSON format
    print(json.dumps(hotel_data, indent=2))

if __name__ == "__main__":
    asyncio.run(run())

# class InstagramProfileScraper():

#     def __init__(self) -> None:

#         self.xhr_page = {}
#         self.xhr_comments = {}
#         self.last_date = datetime.now()
#         self.name = ""

#         self.user_agents = [
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
#             "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15",
#             # Ajoutez d'autres user-agents ici
#         ]
#         user_agent = random.choice(self.user_agents)


#         self.playwright = sync_playwright().start()
#         self.browser = self.playwright.chromium.launch(
#             # proxy={'server':'socks5://127.0.0.1:9150'},
#             headless=False, args=['--start-maximized'])
#         self.context = self.browser.new_context(
#             user_agent=user_agent,
#             no_viewport=True,
#             java_script_enabled=True
#             )
#         self.page = self.context.new_page()

#         self.urls = [
#             {'url': 'https://www.tripadvisor.fr/Hotel_Review-g187140-d313054-Reviews-Hotel_du_Golfe-Ajaccio_Communaute_d_Agglomeration_du_Pays_Ajaccien_Corse_du_Sud_Corsica.html', 'settings': 144}, 
#             {'url': 'https://www.tripadvisor.fr/Hotel_Review-g666541-d623991-Reviews-Hotel_Dolce_Notte-Saint_Florent_Haute_Corse_Corsica.html', 'settings': 137}, 
#             {'url': 'https://www.tripadvisor.fr/Hotel_Review-g196707-d7120453-Reviews-Hotel_Ibiza-Les_Deux_Alpes_Isere_Auvergne_Rhone_Alpes.html', 'settings': 70}, 
#             {'url': 'https://www.tripadvisor.fr/Attraction_Review-g187261-d2463830-Reviews-ESF_Chamonix_Ski_and_Guide_Company-Chamonix_Haute_Savoie_Auvergne_Rhone_Alpes.html', 'settings': 64}, 
#             {'url': 'https://www.tripadvisor.fr/Restaurant_Review-g187261-d10491718-Reviews-La_Fine_Bouche-Chamonix_Haute_Savoie_Auvergne_Rhone_Alpes.html', 'settings': 63}, 
#             {'url': 'https://www.tripadvisor.fr/Restaurant_Review-g187261-d13294436-Reviews-Le_Comptoir_des_Alpes-Chamonix_Haute_Savoie_Auvergne_Rhone_Alpes.html#photos;aggregationId=101&albumid=101&filter=7&ff=466724336', 'settings': 62}, 
#             {'url': 'https://www.tripadvisor.fr/Hotel_Review-g187261-d471965-Reviews-Pierre_Vacances_Residence_La_Riviere-Chamonix_Haute_Savoie_Auvergne_Rhone_Alpes.html#/media/471965/303132012:p/?albumid=101&type=0&category=101', 'settings': 56}, 
#             {'url': 'https://www.tripadvisor.fr/Hotel_Review-g187261-d558174-Reviews-Grand_Hotel_des_Alpes-Chamonix_Haute_Savoie_Auvergne_Rhone_Alpes.html', 'settings': 55}, 
#             {'url': 'https://www.tripadvisor.fr/Restaurant_Review-g1551846-d1555394-Reviews-Le_Lido-Tresserve_Savoie_Auvergne_Rhone_Alpes.html', 'settings': 44}, 
#             {'url': 'https://www.tripadvisor.fr/Attraction_Review-g187261-d12123950-Reviews-Office_de_Tourisme_de_Chamonix_Mont_blanc-Chamonix_Haute_Savoie_Auvergne_Rhone_A.html', 'settings': 38}, 
#             {'url': 'https://www.tripadvisor.fr/Hotel_Review-g1056032-d1055274-Reviews-Madame_Vacances_Les_Chalets_de_Berger-La_Feclaz_Savoie_Auvergne_Rhone_Alpes.html', 'settings': 14}, 
#             {'url': 'https://www.tripadvisor.fr/Hotel_Review-g8309764-d239781-Reviews-Chateau_de_Candie-Chambery_Savoie_Auvergne_Rhone_Alpes.html', 'settings': 6}, 
#             {'url': 'https://www.tripadvisor.fr/Attraction_Review-g8309764-d15690584-Reviews-MV_Transport-Chambery_Savoie_Auvergne_Rhone_Alpes.html', 'settings': 1}
#         ]

#     def clear_page_history(self):
#         self.page.clear_cookies()
#         self.page.clear_cache()

#     def execute(self):
#         for item in self.urls:
#             self.page.mouse.move(random.randint(10, 500), random.randint(5, 100))
#             self.page.goto(item['url'], timeout=10000)
#             time.sleep(10)



# class TripadvisorScraper(object):

#     def __init__(self) -> None:
        
#         user_agents = [
#             "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
#         ]
                
#         self.chrome_options = webdriver.ChromeOptions()
#         self.chrome_options.add_argument("--disable-geolocation")
#         self.chrome_options.add_argument('--ignore-certificate-errors')
#         self.chrome_options.add_argument('--disable-fingerprinting')
#         # self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
#         self.chrome_options.add_argument('--disable-gpu')
#         self.chrome_options.add_argument('--enable-javascript')
#         # self.chrome_options.add_experimental_option('excludeSwitch',['enable-logging']) 
#         self.chrome_options.add_argument('--log-level=3') 
#         self.chrome_options.add_argument(f"user-agent={random.choices(user_agents)}")
#         # self.chrome_options.add_argument('--incognito')


#         self.urls = [
#             {'url': 'https://www.tripadvisor.fr/Hotel_Review-g187140-d313054-Reviews-Hotel_du_Golfe-Ajaccio_Communaute_d_Agglomeration_du_Pays_Ajaccien_Corse_du_Sud_Corsica.html', 'settings': 144}, 
#             {'url': 'https://www.tripadvisor.fr/Hotel_Review-g666541-d623991-Reviews-Hotel_Dolce_Notte-Saint_Florent_Haute_Corse_Corsica.html', 'settings': 137}, 
#             {'url': 'https://www.tripadvisor.fr/Hotel_Review-g196707-d7120453-Reviews-Hotel_Ibiza-Les_Deux_Alpes_Isere_Auvergne_Rhone_Alpes.html', 'settings': 70}, 
#             {'url': 'https://www.tripadvisor.fr/Attraction_Review-g187261-d2463830-Reviews-ESF_Chamonix_Ski_and_Guide_Company-Chamonix_Haute_Savoie_Auvergne_Rhone_Alpes.html', 'settings': 64}, 
#             {'url': 'https://www.tripadvisor.fr/Restaurant_Review-g187261-d10491718-Reviews-La_Fine_Bouche-Chamonix_Haute_Savoie_Auvergne_Rhone_Alpes.html', 'settings': 63}, 
#             {'url': 'https://www.tripadvisor.fr/Restaurant_Review-g187261-d13294436-Reviews-Le_Comptoir_des_Alpes-Chamonix_Haute_Savoie_Auvergne_Rhone_Alpes.html#photos;aggregationId=101&albumid=101&filter=7&ff=466724336', 'settings': 62}, 
#             {'url': 'https://www.tripadvisor.fr/Hotel_Review-g187261-d471965-Reviews-Pierre_Vacances_Residence_La_Riviere-Chamonix_Haute_Savoie_Auvergne_Rhone_Alpes.html#/media/471965/303132012:p/?albumid=101&type=0&category=101', 'settings': 56}, 
#             {'url': 'https://www.tripadvisor.fr/Hotel_Review-g187261-d558174-Reviews-Grand_Hotel_des_Alpes-Chamonix_Haute_Savoie_Auvergne_Rhone_Alpes.html', 'settings': 55}, 
#             {'url': 'https://www.tripadvisor.fr/Restaurant_Review-g1551846-d1555394-Reviews-Le_Lido-Tresserve_Savoie_Auvergne_Rhone_Alpes.html', 'settings': 44}, 
#             {'url': 'https://www.tripadvisor.fr/Attraction_Review-g187261-d12123950-Reviews-Office_de_Tourisme_de_Chamonix_Mont_blanc-Chamonix_Haute_Savoie_Auvergne_Rhone_A.html', 'settings': 38}, 
#             {'url': 'https://www.tripadvisor.fr/Hotel_Review-g1056032-d1055274-Reviews-Madame_Vacances_Les_Chalets_de_Berger-La_Feclaz_Savoie_Auvergne_Rhone_Alpes.html', 'settings': 14}, 
#             {'url': 'https://www.tripadvisor.fr/Hotel_Review-g8309764-d239781-Reviews-Chateau_de_Candie-Chambery_Savoie_Auvergne_Rhone_Alpes.html', 'settings': 6}, 
#             {'url': 'https://www.tripadvisor.fr/Attraction_Review-g8309764-d15690584-Reviews-MV_Transport-Chambery_Savoie_Auvergne_Rhone_Alpes.html', 'settings': 1}
#         ]
#         self.url = ""

#     def use_new_driver(self):
#         try:
#             self.driver.close()
#             self.driver.quit()
#         except:
#             pass
#         self.driver = webdriver.Chrome(options=self.chrome_options)
        
#     def get_search_key(self) -> str:
#         keys = self.url[self.url.index('Reviews-') + 8:len(self.url)-5].replace('_', '+') + "+tripadvisor"
#         return keys

#     def make_search(self) -> object | None:
#         search_key = self.get_search_key()
#         self.driver.get(f"https://www.google.com/search?q={search_key}")
#         time.sleep(8)
#         elements = self.driver.find_elements(By.CSS_SELECTOR, "div.srKDX.cvP2Ce")
#         for i in range(len(elements)):
#             tag_a = BeautifulSoup(elements[i].get_attribute('innerHTML'), 'lxml').find_all('a', href=True)
#             for a in tag_a:
#                 try:
#                     if 'tripadvisor' in a['href']:
#                         find = 0
#                         for item in search_key.split(' '):
#                             if item.lower() in a['href'].lower():
#                                 find += 1
#                         print(f"{int(find / len(search_key.split(' '))) * 100 } %")
#                         if (find / len(search_key.split(' '))) >= 0.6 and a['href']:
#                             print(a['href'])
#                             return elements[i]
#                 except:
#                     pass

#     def set_url(self, item:dict):
#         self.url = item['url']

#     def check_paginator(self) -> bool:
#         try:
#             self.driver.find_element(By.XPATH, "//a[contains(@aria-label, 'Page suivante')]")
#             return True
#         except NoSuchElementException:
#             return False
    
#     def go_next_page(self):
#         try:
#             next_page = self.driver.find_element(By.XPATH, "//a[contains(@aria-label, 'Page suivante')]")
#             next_page.click()
#             self.driver.implicitly_wait(30)
#         except NoSuchElementException:
#             return False

#     def extract(self):
#         print('extracting data')

#     def navigate(self):
#         while self.check_paginator():
#             self.go_next_page()
#             time.sleep(5)
#             self.extract()

#     def execute(self):
#         for item in self.urls:
#             self.set_url(item)
#             self.use_new_driver()
#             element = self.make_search()
#             if element:
#                 element.find_element(By.TAG_NAME, 'a').click()
#             else:
#                 self.driver.get(self.url)
#             time.sleep(5)
#             self.navigate()



        
