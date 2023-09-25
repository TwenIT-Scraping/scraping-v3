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
import instaloader
from models import create


class Instagram(Scraping):
    def __init__(self, url: str, establishment: str):
        super().__init__(in_background=False, url=url, establishment=establishment)
        
        split_url = self.url.split('/')
        self.userprofile = split_url[-1] if split_url[-1] != '' else split_url[-2]

        bot = instaloader.Instaloader()
        self.profile = instaloader.Profile.from_username(bot.context, self.userprofile)

        self.posts = []

    def load_posts(self, page_id):
        for p in self.posts:
            p["socialPage"] = f"/api/social_pages/{page_id}"

    def extract(self) -> None:
        try:
            for post in self.profile.get_posts():
                self.posts.append({
                    "title": "",
                    "comments": post.comments,
                    "likes": post.likes,
                    "share": 0,
                    "publishedAt": post.date.strftime("%Y-%m-%d"),
                    "socialPage": f"/api/social_pages/33"
                })
            
            self.data = {
                "source": "instagram",
                "followers": self.profile.followers,
                "likes": 0,
                "posts": len(self.posts),
                "establishment": f"/api/establishments/{self.establishment}",
            }
            
        except Exception as e:
            print(e)

    def save(self):
        print("** Upload page")
        page = create(entity='social_pages', data=self.data)
        # page.print()
        res = page.save()
        print(res)
        
        self.load_posts(res['id'])
        # self.load_posts(144)

        for p in self.posts:
            post = create(entity='social_posts', data=p)
            # post.print()
            print(post.save())


instance = Instagram(url="https://www.instagram.com/thechelseapinesinn/", establishment=33)
instance.execute()