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
from api import ERApi
import json
from tools import shortmonths_fr


def format_number(number):
    nb = number.split()
    if len(nb) == 3:
        if ',' in nb[0] and nb[1] == 'k':
            return nb[0].replace(',', '') + '00'
        elif nb[1] == 'k':
            return nb[0] + '000'
    else:
        return nb[0]


class Youtube(Scraping):
    def __init__(self, url: str, establishment: str):
        super().__init__(url=url, in_background=False, establishment=establishment)
        self.items = []
        self.data = {}

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

        total = max_item if max_item <= 20 else 20

        for container in post_containers:
            try:
                for item in container.find_all('ytd-rich-item-renderer'):
                    url = item.find('a', {'id': 'video-title-link'})['href']
                    post_urls.append(f"https://www.youtube.com{url}")
                    count += 1

                    if count == total: 
                        break

            except Exception as e:
                pass

        return post_urls
    
    def scrap_item(self, item_url):
        self.scrap(item_url)
        
        for i in range(3):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)

        self.driver.find_element(By.XPATH, '//tp-yt-paper-button[@id="expand"]').click()
        time.sleep(2)

        data = {
            "share": 0,
            "socialPage": "/api/social_pages/10"
        }

        try:
            # Wait until the element is visible
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, 'comments')))
            soup  = BeautifulSoup(self.driver.page_source, 'lxml')
            container = soup.find('div', {'id': 'primary-inner'})
            
            title = container.find('div', {'id': 'title'}).text.strip()
            likes = container.find('div', {'id': 'segmented-like-button'}).find('span').text.strip()
            comments = container.find('ytd-comments', {'id': 'comments'}).find('h2', {'id': 'count'}).find_all('span')[0].text.strip() \
                if container.find('ytd-comments', {'id': 'comments'}) and container.find('ytd-comments', {'id': 'comments'}).find('h2', {'id': 'count'}) else "0"
            date = container.find('yt-formatted-string', {'id': 'info'}).find_all('span')[2].text.strip()
            month = shortmonths_fr[date.split()[1]]
            day = date.split()[0]
            year = date.split()[2]

            data['title'] = title
            data['likes'] = int(likes)
            data['comments'] = int(comments)
            data['publishedAt'] = "%s-%s-%s"%(year, month, day)

            return data

        except Exception as e:
            print(e)
            pass

        return None

    def extract(self) -> None:
        try:
            time.sleep(10)
            soup  = BeautifulSoup(self.driver.page_source, 'lxml')
            followers = soup.find('yt-formatted-string', {'id': 'subscriber-count'}).text.strip()
            nb_followers = int(format_number(followers))
            
            posts = soup.find('yt-formatted-string', {'id': 'videos-count'}).text.strip()
            nb_posts = int(format_number(posts))

            posts = self.get_posts_url(nb_posts)
            items = []
            
            for item in posts:
                d = self.scrap_item(item)
                d and items.append(d)

            data = {
                "source": "youtube",
                "followers": nb_followers,
                "likes": 0,
                "posts": nb_posts,
                "establishment": f"/api/establishments/{self.establishment}",
            }

            self.data = data
            self.items = items

        except Exception as e:
            print('extraction file')
            print(e)

    def save(self):
        print("** Upload page")
        page = create(entity='social_posts', data=self.data)
        res = page.save()
        print("**** Upload posts")
        for p in self.items:
            p["socialPage"] = f"/api/social_pages/{res['id']}"
            print(p)
            post = create(entity='social_posts', data=p)
            print(post.save())

sites = [
    {
        "url": "https://www.youtube.com/@chateaudecandie3219",
        "estab": 6
    },
    {
        "url": "https://www.youtube.com/@hotellabelleetoile1071",
        "estab": 9
    },
    {
        "url": "https://www.youtube.com/@HyattUnionSquareNYC",
        "estab": 34
    },
    {
        "url": "https://www.youtube.com/@washingtonsquarehotel4124",
        "estab": 30
    },
    {
        "url": "https://www.youtube.com/@belambrahotelsresortsinfra1781",
        "estab": 28
    },
    {
        "url": "https://www.youtube.com/@hotelchaletmounierrestaura2220",
        "estab": 26
    },
    {
        "url": "https://www.youtube.com/@cotebrunehotelspa918",
        "estab": 25
    },
    {
        "url": "https://www.youtube.com/@hotelcampanileparisbercyvi730",
        "estab": 23
    },
    {
        "url": "https://www.youtube.com/@lacotelarete8047",
        "estab": 19
    }
]

instance = Youtube(url="", establishment=-1)
for site in sites:
    instance.set_establishment(site["estab"])
    instance.set_url(site["url"])
    instance.execute()
    instance.save()

def post_from_file(filename=""):
    instance = ERApi(method='post', entity='social_posts')
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            items = json.load(file)
            for item in items:
                instance.set_body(item)
                instance.execute()
    except Exception as e:
        print(e)

def post_tweet_file(filename=""):
    instance_post = ERApi(method='post', entity='social_posts')
    instance_page = ERApi(method='post', entity='social_pages')
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            pages = json.load(file)
            page_id = 17
            for page in pages:
                print("post page: ", page["name"])
                page_body = {
                    "source": page["source"],
                    "followers": page["followers"],
                    "likes": 0,
                    "posts": len(page["tweets"]),
                    "establishment": page["establishment"]
                } 
                instance_page.set_body(page_body)
                res = instance_page.execute()
                print(res.json())
                print("--------- Post establishment posts ----------")
                for post in page["tweets"]:
                    print("-> ", post["post_text"])
                    post_body = {
                        "title": post["post_text"],
                        "comments": post["post_reply"],
                        "likes": post["favorite_count"],
                        "share": post["post_retweet"],
                        "publishedAt": datetime.strptime(post["created_at"].replace(' +0000', ''), '%c').strftime("%Y-%m-%d"),
                        "socialPage": f"/api/social_pages/{page_id}"
                    }
                    instance_post.set_body(post_body)
                    instance_post.execute()
                page_id += 1
    except Exception as e:
        print(e)

# post_from_file('fb_brune.json')
# post_tweet_file('twitter_scrap.json')
