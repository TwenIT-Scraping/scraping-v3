import json
import os
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from nested_lookup import nested_lookup
from datetime import datetime, timedelta
import time
from scraping import Scraping
import re
from progress.bar import ChargingBar, FillingCirclesBar
from os import environ


class YoutubeProfileScraper(Scraping):

    def __init__(self, items: list = []) -> None:
        super().__init__(items)
        self.set_credentials('youtube')

        self.hotel_page_urls = []
        self.xhr_page = []
        self.xhr_posts = []
        self.xhr_comments = []
        self.data = []

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False, args=['--start-maximized'])
        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()
        self.post_index = 0
        self.open_post = False

    def clean_data(self):
        self.xhr_page = []
        self.xhr_posts = []
        self.xhr_comments = []
        self.data = []
        self.posts = []
        self.page_data = {}

    def stop(self):
        self.context.close()

    def create_logfile(self, logfile_name: str) -> None:
        pass

    def load_history(self) -> None:
        pass

    def set_history(self, key: str, value: any) -> None:
        pass

    def goto_login(self) -> None:
        self.page.goto("https://www.youtube.com", timeout=30000)
        # self.page.wait_for_timeout(30000)

    def open_posts(self):
        try:
            posts_items = self.page.locator(
                "ytd-rich-item-renderer ytd-rich-grid-media").all()

            items = [item.locator('ytd-thumbnail a').get_attribute("href")
                     for item in posts_items]
            items_date = [item.locator(
                'div#metadata span.inline-metadata-item:last-of-type').text_content() for item in posts_items]

            for index in range(len(items)):
                self.page.goto(
                    f"https://www.youtube.com{items[index]}", timeout=30000)
                self.page.wait_for_timeout(20000)
                self.scroll_down_page(iteration=1, step=500)
                self.page.wait_for_timeout(20000)
                self.scroll_down_page(iteration="infinite")
                self.page.wait_for_timeout(20000)
                self.extract_post_data(date=items_date[index])

            self.page_data['posts'] = len(self.posts)
        except Exception as e:
            print(e)
            pass

    def complete_source_data(self):

        posts = []

        coms = self.xhr_comments

        for item in self.xhr_posts:
            for p in item:
                posts.append(p)

        self.xhr_posts = posts

    def goto_youtube_page(self) -> None:
        if '.com/channel/@socrugby-chambery4833' in self.url:
            self.url = self.url.replace('.com/channel/@socrugby-chambery4833', '.com/@socrugby-chambery4833')
        self.page.goto(f"{self.url}/videos", timeout=50000)

        self.page.wait_for_timeout(6000)
        time.sleep(3)
        self.extract_page_data()
        print(self.page_data)
        #self.scroll_down_page(iteration="infinite")
        #self.open_posts()
        # self.complete_source_data()

    def format_number(self, number):
        splited_value = number.split(
            '\xa0') if '\xa0' in number else number.split(' ')
        if len(splited_value) == 3:
            if splited_value[1].lower() == "k":
                return int(float(splited_value[0].replace(',', '.'))*1000)
            if splited_value[1].lower() == 'm':
                return int(float(splited_value[0].replace(',', '.'))*1000000)
        if len(splited_value) == 2:
            if 'm ' in splited_value[1].lower():
                return int(float(splited_value[0].replace(',', '.'))*1000000)

            return int(float(splited_value[0].replace(',', '.')))

        return splited_value[0].replace(',', '.')

    def scroll_down_page(self, iteration='infinite', step=15000) -> None:

        if iteration == 'infinite':
            prev_height = None

            while True:
                self.page.mouse.wheel(0, step)
                time.sleep(5)

                curr_height = self.page.evaluate(
                    '(window.innerHeight + window.scrollY)')

                if not prev_height:
                    prev_height = curr_height
                elif prev_height == curr_height:
                    break
                else:
                    prev_height = curr_height
        else:

            for i in range(iteration):  # make the range as long as needed
                self.page.mouse.wheel(0, step)
                time.sleep(5)

    def extract_page_data(self) -> None:

        try:
            soupe = BeautifulSoup(self.page.content(), 'lxml')
            """name = soupe.find('yt-formatted-string', {'class': "ytd-channel-name"}).text.strip() \
                if soupe.find('yt-formatted-string', {'class': "ytd-channel-name"}) else ''"""
            name = self.page.locator('xpath=//*[@id="page-header"]/yt-page-header-renderer/yt-page-header-view-model/div/div[1]/div/yt-dynamic-text-view-model/h1/span').inner_text().strip()
            """followers = soupe.find('yt-formatted-string', {'id': "subscriber-count"}).text.strip() \
                if soupe.find('yt-formatted-string', {'id': "subscriber-count"}) else ''"""
            followers = self.page.locator('xpath=//*[@id="page-header"]/yt-page-header-renderer/yt-page-header-view-model/div/div[1]/div/yt-content-metadata-view-model/div[2]/span[1]').inner_text().strip()

            self.page_data = {
                'followers': self.format_number(followers),
                'likes': None,
                'source': "youtube",
                'establishment': f'api/establishments/{self.establishment}',
                'name': f"youtube_{name}",
            }
            self.source = self.page_data['source']

        except Exception as e:
            print(e)
            pass

    def extract_post_data(self, date) -> None:
        def format_date(string_date):
            day_terms = ['day', 'days', 'jour', 'jours']
            today_terms = ['seconde', 'secondes', 'minute',
                           'minutes', 'hours', 'hour', 'heure', 'heures']
            week_terms = ['week', 'weeks', 'semaine', 'semaines']
            month_terms = ['month', 'months', 'mois']
            year_terms = ['year', 'years', 'an', 'ans']

            if string_date != "":

                splited_date = string_date.lower().split(' ')

                value = list(filter(lambda x: x.isnumeric(), splited_date))[0]

                try:

                    if any(x in today_terms for x in splited_date):
                        return datetime.now()

                    if any(x in day_terms for x in splited_date):
                        return datetime.now() + timedelta(days=-int(value))

                    if any(x in week_terms for x in splited_date):
                        return datetime.now() + timedelta(weeks=-int(value))

                    if any(x in month_terms for x in splited_date):
                        return datetime.now() + timedelta(days=-int(value)*30)

                    if any(x in year_terms for x in splited_date):
                        return datetime.now() + timedelta(days=-int(value)*365)

                    else:
                        print("else")

                except Exception as e:
                    print(e)

        soupe = BeautifulSoup(self.page.content(), 'lxml')

        try:
            title = soupe.find('ytd-watch-metadata', {'class': 'watch-active-metadata'}).find('div', {'id': "title"}).text.strip() \
                if soupe.find('ytd-watch-metadata', {'class': 'watch-active-metadata'}) and soupe.find('ytd-watch-metadata', {'class': 'watch-active-metadata'}).find('div', {'id': "title"}) else ''
            likes = soupe.find('like-button-view-model').find('div', {'class': "yt-spec-button-shape-next__button-text-content"}).text.strip() \
                if soupe.find('like-button-view-model') and soupe.find('like-button-view-model').find('div', {'class': "yt-spec-button-shape-next__button-text-content"}) else ''
            author = soupe.find('ytd-channel-name', {'id': 'channel-name'}).text.strip() \
                if soupe.find('ytd-channel-name', {'id': 'channel-name'}) else ""
            published_date = format_date(date).strftime('%d/%m/%Y')

            comments = soupe.find_all('ytd-comment-thread-renderer')

            comment_values = []

            for comment in comments:
                try:
                    comment_values.append({
                        'comment': comment.find('yt-formatted-string', {'id': 'content-text'}).text.strip() if comment.find('yt-formatted-string', {'id': 'content-text'}) else "",
                        'published_at': format_date(comment.find('yt-formatted-string', {'class': 'published-time-text'}).text.strip()).strftime("%d/%m/%Y") if comment.find('yt-formatted-string', {'class': 'published-time-text'}) else "",
                        'likes': self.format_number(comment.find('span', {'id': 'vote-count-middle'}).text.strip()) if comment.find('span', {'id': 'vote-count-middle'}) else 0,
                        'author': comment.find('a', {'id': 'author-text'}).text.strip() if comment.find('a', {'id': 'author-text'}) else ""
                    })
                except Exception as e:
                    print(e)
                    pass

            self.posts.append({
                "author": author,
                "publishedAt": published_date,
                "description": title,
                "reaction": likes,
                "comments": len(comment_values),
                "shares": 0,
                "hashtag": "",
                "comment_values": comment_values
            })

        except Exception as e:
            print(e)
            pass

    def switch_acount(self) -> None:
        pass

    def execute(self) -> None:
        # progress = ChargingBar('Preparing ', max=3)
        # self.set_current_credential(0)
        # progress.next()
        print(" | Open login page")
        self.goto_login()
        output_files = []
        i = 1
        for item in self.items:
            p_item = FillingCirclesBar(item['establishment_name'], max=3)
            self.set_item(item)
            self.clean_data()
            p_item.next()
            print(" | Open page")
            self.goto_youtube_page()
            p_item.next()
            # print(" | Extracting")
            # self.extract_data()
            #p_item.next()
            print(" | Saving")
            output_files.append(self.save())
            p_item.next()
            print(" | Saved")
            if i == 1:
                break
        self.stop()

        return output_files
