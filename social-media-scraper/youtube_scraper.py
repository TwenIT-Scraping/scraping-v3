import json
import os
from playwright.sync_api import sync_playwright
from nested_lookup import nested_lookup
from datetime import datetime
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

    def resolve_loginform(self) -> None:
        self.fill_loginform()

    def goto_login(self) -> None:
        self.page.goto("https://www.youtube.com", timeout=30000)
        self.page.wait_for_timeout(30000)

    def fill_loginform(self) -> None:
        self.page.wait_for_selector("[name='username']", timeout=30000)
        self.page.locator("[name='username']").click()
        time.sleep(.5)
        self.page.fill("[name='username']", self.current_credential['email'])
        time.sleep(.3)
        self.page.locator("[name='password']").click()
        time.sleep(.2)
        self.page.fill("[name='password']",
                       self.current_credential['password'])
        time.sleep(.1)
        self.page.locator("[type='submit']").click()
        self.page.wait_for_timeout(70000)

    def intercept_response(self, response) -> None:
        """capture all background requests and save them"""
        response_type = response.request.resource_type

        if response_type == "fetch":

            # => /next?prettyPrint=false
            self.xhr_comments.append(response.url)

            # if 'guide?prettyPrint=false' in response.url:
            #     self.xhr_page = response.json()

            if 'next?prettyPrint=false' in response.url:
                self.xhr_posts.append(nested_lookup(
                    key="compactVideoRenderer", document=response.json()))

    def open_posts(self):
        posts_items = self.page.locator(
            "ytd-rich-item-renderer ytd-rich-grid-media ytd-thumbnail a").all()

        for item in posts_items:
            href = item.get_attribute("href")
            self.page.goto(f"https://www.youtube.com{href}", timeout=30000)
            self.page.wait_for_timeout(30000)
            self.scroll_down_page()

    def complete_source_data(self):

        posts = nested_lookup(key='node', document=self.xhr_posts)
        coms = self.xhr_comments

        for index in range(len(coms)):
            try:
                pk = coms[index]['caption']['pk']

                print(pk)

                if pk != posts[index]['caption']['pk']:
                    for post in posts:
                        if "caption" in post.keys() and post["caption"]["pk"] == pk:
                            post["comments"] = coms[index]
                else:
                    posts[index]["comments"] = coms[index]

            except Exception as e:
                print(e)
                pass

        self.xhr_posts = posts

    def goto_youtube_page(self) -> None:
        self.page.on("response", self.intercept_response)
        self.page.goto(f"{self.url}/videos", timeout=50000)
        self.page.wait_for_timeout(6000)
        time.sleep(3)
        self.scroll_down_page()
        self.open_posts()
        # self.complete_source_data()

    def scroll_down_page(self) -> None:
        for i in range(5):  # make the range as long as needed
            print("scrolling down ...")
            self.page.mouse.wheel(0, 15000)
            time.sleep(5)

    def get_json_content(self, item: object, key: str) -> object:
        try:
            return item[key]
        except KeyError:
            return ''

    def extract_data(self) -> None:

        with open(f"{environ.get('SOCIAL_FOLDER')}/{self.establishment}_youtubeposts.json", 'w') as foutput:
            json.dump(self.xhr_posts, foutput, indent=4, sort_keys=True)

        # with open(f"{environ.get('SOCIAL_FOLDER')}/{self.establishment}_youtubefetchs.json", 'w') as foutput:
        #     json.dump(self.xhr_comments, foutput, indent=4, sort_keys=True)

        # with open(f"{environ.get('SOCIAL_FOLDER')}/{self.establishment}_youtubepage.json", 'w') as foutput:
        #     json.dump(self.xhr_page, foutput, indent=4, sort_keys=True)

        posts = self.xhr_posts

        # for post in posts:

        #     if type(post["comments"]) != list:

        #         comments = post["comments"]["comments"]
        #         comment_values = []

        #         for cmt in comments:
        #             try:
        #                 comment_values.append({
        #                     'comment': cmt["text"],
        #                     'published_at': datetime.fromtimestamp(cmt["created_at"]).strftime("%d/%m/%Y"),
        #                     'likes': cmt["comment_like_count"],
        #                     'author': cmt["user"]["full_name"]
        #                 })
        #             except Exception as e:
        #                 print(e)
        #                 pass

        #         try:
        #             self.posts.append({
        #                 "author": post["owner"]["full_name"],
        #                 "publishedAt": datetime.fromtimestamp(post["comments"]["caption"]["created_at"]).strftime("%d/%m/%Y"),
        #                 "description": post["caption"]["text"],
        #                 "reaction": post["like_count"],
        #                 "comments": len(comment_values),
        #                 "shares": 0,
        #                 "hashtag": "",
        #                 "comment_values": comment_values
        #             })

        #         except Exception as e:
        #             print(e)
        #             pass

        print("posts traités: ", len(self.posts))

        try:
            self.page_data = {
                'followers': nested_lookup(key='edge_followed_by', document=self.xhr_page)[0]["count"],
                'likes': 0,
                'source': "instagram",
                'establishment': self.establishment,
                'name': f"instagram_{nested_lookup(key='full_name', document=self.xhr_page)[0]}",
                'posts': len(self.posts)
            }

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
        # progress.next()
        # print(" | Fill login page")
        # self.fill_loginform()
        # # progress.next()
        # print(" | Logged in!")
        output_files = []
        for item in self.items:
            # p_item = FillingCirclesBar(item['establishment_name'], max=3)
            self.set_item(item)
            self.clean_data()
            # p_item.next()
            print(" | Open page")
            self.goto_youtube_page()
        #     p_item.next()
            print(" | Extracting")
            self.extract_data()
        #     p_item.next()
        #     print(" | Saving")
        #     output_files.append(self.save())
        #     p_item.next()
        #     print(" | Saved")

        self.stop()

        # return output_files
