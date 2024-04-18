import json
import os
from playwright.sync_api import sync_playwright
from nested_lookup import nested_lookup
from datetime import datetime, timedelta
import time
from scraping import Scraping
import re
from progress.bar import ChargingBar, FillingCirclesBar


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
            if 'web_profile_info' in response.url:
                self.xhr_page = response.json()['data']['user']
            if 'graphql' in response.url:
                if 'xdt_api__v1__feed__user_timeline_graphql_connection' in response.json()['data']:
                    [self.xhr_posts.append(item) for item in response.json(
                    )['data']['xdt_api__v1__feed__user_timeline_graphql_connection']['edges']]

            if 'comments/' in response.url:
                try:
                    self.xhr_comments.append(response.json())
                except Exception as e:
                    print(e)
                    pass

    def open_posts(self):
        # posts = self.page.locator(
        #     "div._aabd._aa8k.x2pgyrj.xbkimgs.xfllauq.xh8taat.xo2y696 a.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz._a6hd").all()
        posts = self.page.locator(
            "div._ac7v.xzboxd6.xras4av.xgc1b0m a.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz._a6hd").all()

        # print("posts found: ", len(posts))

        try:
            posts[0].click()
        except Exception as e:
            print(e)
            pass

        time.sleep(3)

        p = 1

        while True:

            btns = self.page.locator(
                "div.x1n2onr6.xzkaem6").locator("button._abl-").all()

            # print("boutons: ", len(btns))

            for btn in btns:
                if len(btn.locator('svg').all()) > 0:
                    # print('Buttons found!!!')
                    for svg in btn.locator('svg').all():
                        if svg.get_attribute('aria-label') == "Suivant" or svg.get_attribute('aria-label') == "Next":
                            btn.click()
                            time.sleep(3)
                            break

            self.page.wait_for_timeout(2000)
            p += 1

            if p > len(self.xhr_posts) or p > 100:
                break

    def complete_source_data(self):

        posts = nested_lookup(key='node', document=self.xhr_posts)
        coms = self.xhr_comments

        for index in range(len(coms)):
            try:
                pk = coms[index]['caption']['pk']

                # print(pk)

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

    def extract_data(self) -> None:

        posts = self.xhr_posts

        for post in posts:

            if type(post["comments"]) != list:

                comments = post["comments"]["comments"]
                comment_values = []

                for cmt in comments:
                    try:
                        date = datetime.fromtimestamp(cmt["created_at"])
                        if date >= datetime.now() + timedelta(days=-365):
                            comment_values.append({
                                'comment': cmt["text"],
                                'published_at': date.strftime("%d/%m/%Y"),
                                'likes': cmt["comment_like_count"],
                                'author': cmt["user"]["full_name"]
                            })
                    except Exception as e:
                        print(e)
                        pass

                try:
                    if 'caption' in post.keys() and 'comments' in post.keys() and 'caption' in post['comments'].keys():
                        published_at = datetime.fromtimestamp(
                            post["comments"]["caption"]["created_at"])
                        published_at > (datetime.now() - timedelta(days=365)) and post["owner"]["full_name"] and post["caption"]["text"] and self.posts.append({
                            "author": post["owner"]["full_name"],
                            "publishedAt": published_at.strftime("%d/%m/%Y"),
                            "description": post["caption"]["text"],
                            "reaction": post["like_count"],
                            "comments": len(comment_values),
                            "shares": 0,
                            "hashtag": "",
                            "comment_values": comment_values
                        })

                except Exception as e:
                    print(e)
                    pass

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
