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


class InstagramProfileScraper(Scraping):

    def __init__(self, items: list = []) -> None:
        super().__init__(items)
        self.set_credentials('instagram')

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
        self.page.goto(
            "https://www.instagram.com/accounts/login/", timeout=30000)
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

        if response_type == "xhr":
            if 'web_info/?tag_name' in response.url:
                # self.xhr_posts = response.json()
                responses = response.json()
                [self.xhr_posts.append(item) for item in nested_lookup(
                    key='media', document=responses)]
            # if 'graphql' in response.url:
            #     if 'xdt_api__v1__feed__user_timeline_graphql_connection' in response.json()['data']:
            #         [self.xhr_posts.append(item) for item in response.json(
            #         )['data']['xdt_api__v1__feed__user_timeline_graphql_connection']['edges']]

            if 'comments/' in response.url:
                try:
                    self.xhr_comments.append(response.json())
                except Exception as e:
                    print(e)
                    pass

    def open_posts(self):
        posts = self.page.locator(
            "main a.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz._a6hd").all()

        posts[0].click()
        self.page.wait_for_timeout(2000)
        time.sleep(3)

        self.open_comments()

        btns = self.page.locator(
            "div.x1n2onr6.xzkaem6").locator("button._abl-").all()

        p = 1

        while True:
            print(p)

            for btn in btns:
                if len(btn.locator('svg').all()) > 0:
                    for svg in btn.locator('svg').all():
                        if svg.get_attribute('aria-label') == "Suivant":
                            btn.click()
                            time.sleep(3)
                            break

            self.page.wait_for_timeout(2000)
            self.open_comments()
            p += 1

            if p > len(self.xhr_posts) or p > 500:
                break

    def open_comments(self):

        btns = self.page.locator(
            "ul._a9z6._a9za").locator("button._abl-").all()

        while True:
            no_next = True

            for btn in btns:
                if len(btn.locator('svg').all()) > 0:
                    for svg in btn.locator('svg').all():
                        if svg.get_attribute('aria-label') == "Load more comments" or svg.get_attribute('aria-label') == "Charger d’autres commentaires":
                            btn.click()
                            time.sleep(3)
                            no_next = False
                            break
                else:
                    no_next = True

            if no_next:
                break

            self.page.wait_for_timeout(2000)

    def complete_source_data(self):

        def find_post_by_pk(posts, pk):
            for index in range(len(posts)):
                if "caption" in posts[index].keys() and posts[index]["caption"]["pk"] == pk:
                    return index

            return -1

        posts = self.xhr_posts
        coms = self.xhr_comments

        for index in range(len(coms)):
            try:
                if index < len(coms) and index < len(posts):
                    pk = coms[index]['caption']['pk']

                    if pk != posts[index]['caption']['pk']:
                        post_index = find_post_by_pk(
                            posts, coms[index]['caption']['pk'])
                        if post_index != -1:
                            [posts[post_index]["comments"].append(
                                comment) for comment in coms[index]["comments"]]
                    else:
                        [posts[index]["comments"].append(
                            comment) for comment in coms[index]["comments"]]
                else:
                    post_index = find_post_by_pk(
                        posts, coms[index]['caption']['pk'])
                    if post_index != -1:
                        [posts[post_index]["comments"].append(
                            comment) for comment in coms[index]["comments"]]

            except Exception as e:
                print(e)
                pass

        self.xhr_posts = posts

    def goto_insta_page(self) -> None:
        self.page.on("response", self.intercept_response)
        self.page.goto(self.url, timeout=50000)
        self.page.wait_for_timeout(6000)
        time.sleep(3)
        # self.scroll_down_page()
        self.open_posts()
        self.complete_source_data()

    def scroll_down_page(self) -> None:
        for i in range(5):
            self.page.evaluate(
                "window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(5000)
            time.sleep(3)

    def get_json_content(self, item: object, key: str) -> object:
        try:
            return item[key]
        except KeyError:
            return ''

    def set_item(self, item):
        super().set_item(item)
        self.hashtag = self.url.split("/")[-2:][0] if self.url.split(
            "/")[-1:][0] == "" else self.url.split("/")[-1:][0]

    def extract_data(self) -> None:

        # with open(f"{environ.get('SOCIAL_FOLDER')}/{hashtag}posts_hashtag.json", 'w') as foutput:
        #     json.dump(self.xhr_posts, foutput, indent=4, sort_keys=True)

        # with open(f"{environ.get('SOCIAL_FOLDER')}/{hashtag}comments_hashtag.json", 'w') as foutput:
        #     json.dump(self.xhr_comments, foutput, indent=4, sort_keys=True)

        print(len(self.xhr_posts), " posts trouvés.")
        print(len(self.xhr_comments), " comments trouvés.")

        with open(f"{environ.get('SOCIAL_FOLDER')}/resultsposts_hashtag.json", 'w') as foutput:
            json.dump(self.xhr_posts, foutput, indent=4, sort_keys=True)

        for post in self.xhr_posts:
            comment_values = []

            for cmt in post["comments"]:
                try:
                    comment_values.append({
                        'comment': cmt["text"],
                        'published_at': datetime.fromtimestamp(cmt["created_at"]).strftime("%d/%m/%Y"),
                        'likes': cmt["comment_like_count"],
                        'author': cmt["user"]["full_name"] if cmt["user"]["full_name"] else cmt["user"]["username"]
                    })
                except Exception as e:
                    print(e)
                    pass

            try:
                self.posts.append({
                    "author": post["owner"]["full_name"] if post["owner"]["full_name"] else post["owner"]["username"],
                    "publishedAt": datetime.fromtimestamp(post["caption"]["created_at"]).strftime("%d/%m/%Y"),
                    "description": post["caption"]["text"],
                    "reaction": post["like_count"],
                    "comments": len(comment_values),
                    "shares": 0,
                    "hashtag": self.hashtag,
                    "comment_values": comment_values
                })

            except Exception as e:
                print(e)
                pass

        print("posts traités: ", len(self.posts))

        self.page_data = {
            'likes': 0,
            'source': "instagram",
            'establishment': self.establishment,
            'posts': len(self.posts)
        }

    def switch_acount(self) -> None:
        pass

    def execute(self) -> None:
        progress = ChargingBar('Preparing ', max=3)
        self.set_current_credential(1)
        progress.next()
        print(" | Open login page")
        self.goto_login()
        progress.next()
        print(" | Fill login page")
        self.fill_loginform()
        progress.next()
        print(" | Logged in!")
        output_files = []
        for item in self.items:
            p_item = FillingCirclesBar(item['establishment_name'], max=3)
            self.set_item(item)
            self.clean_data()
            p_item.next()
            print(" | Open page")
            self.goto_insta_page()
            p_item.next()
            print(" | Extracting")
            self.extract_data()
            p_item.next()
            print(" | Saving")
            output_files.append(self.save())
            p_item.next()
            print(" | Saved")

        self.stop()

        return output_files
