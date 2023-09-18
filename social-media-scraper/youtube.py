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
from models import SocialPage, create


class Youtube(Scraping):
    def __init__(self, url: str, establishment: str):
        super().__init__(url=url, in_background=False, establishment=establishment)

    def execute(self):
        try:
            self.scrap(self.url)
            self.extract()
            # self.save()
            # self.driver.quit()
        except Exception as e:
            print(e)
            self.driver.quit()
            sys.exit("Arret")
    
    def get_posts_url(self, max_item=10):
        post_url = self.url + '/videos'
        self.scrap(post_url)

        time.sleep(10)
        soup  = BeautifulSoup(self.driver.page_source, 'lxml')
        post_containers = soup.find('ytd-rich-grid-row')
        post_urls = []

        count = 0

        for container in post_containers:
            try:
                for item in container.find_all('ytd-rich-item-renderer'):
                    url = item.find('a', {'id': 'video-title-link'})['href']
                    post_urls.append(f"https://www.youtube.com{url}")
                    count += 1

                    if count == max_item: 
                        break

            except Exception as e:
                pass

        return post_urls
    
    def scrap_item(self, item_url):
        self.scrap(item_url)

        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        try:
            # Wait until the element is visible
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, 'comments')))
            soup  = BeautifulSoup(self.driver.page_source, 'lxml')
            container = soup.find('div', {'id': 'primary-inner'})
            
            title = container.find('div', {'id': 'title'}).text.strip()
            likes = container.find('div', {'id': 'segmented-like-button'}).find('span').text.strip()
            try:
                comments = container.find('ytd-comments', {'id': 'comments'}).find('h2', {'id': 'count'}).find_all('span')[0].text.strip()
            except Exception as E:
                print(E)
                print(container.find('ytd-comments', {'id': 'comments'}))

            print('\n')
            # print(title)
            print(title, ' => ', likes, 'likes / ', comments, ' comments')
        except Exception as e:
            print(e)
            pass

    def extract(self) -> None:
        def format_number(number):
            nb = number.split()
            if len(nb) == 3:
                if ',' in nb[0] and nb[1] == 'k':
                    return nb[0].replace(',', '') + '00'
                elif nb[1] == 'k':
                    return nb[0] + '000'
            else:
                return nb[0]

        # self.load_reviews()

        # reviews = []

        try:
            time.sleep(10)
            soup  = BeautifulSoup(self.driver.page_source, 'lxml')
            followers = soup.find('yt-formatted-string', {'id': 'subscriber-count'}).text.strip()
            nb_followers = format_number(followers)
            
            posts = followers = soup.find('yt-formatted-string', {'id': 'videos-count'}).find_all('span')[0].text.strip()
            nb_posts = format_number(posts)

            print(nb_followers, nb_posts)
            posts = self.get_posts_url(2)
            for item in posts:
                self.scrap_item(item)

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

    def save(self):
        page = create('social_posts', {
            "title": "Château de Candie - Hôtel 4**** à Chambéry",
            "comments": 0,
            "likes": 10,
            "share": 0,
            "publishedAt": "2014-07-17",
            "socialPage": "/api/social_pages/2"
        })

        page.save()


instance = Youtube(url="https://www.youtube.com/@MontCorvo", establishment=2)
# instance.execute()
print(instance.save())