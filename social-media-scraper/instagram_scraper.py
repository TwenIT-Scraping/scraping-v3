import json
import os
from playwright.sync_api import sync_playwright
from nested_lookup import nested_lookup
from datetime import datetime, timedelta
import time
from scraping import Scraping
import re
from progress.bar import ChargingBar, FillingCirclesBar


class OldInstagramProfileScraper(Scraping):

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
            if 'query' in response.url:
                try:
                    if response.json()['data']['user']:
                        self.xhr_page = response.json()['data']['user']
                except KeyError:
                    pass

            if 'query' in response.url:
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
        posts = self.page.locator("div._ac7v.xzboxd6.xras4av.xgc1b0m a.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz._a6hd").all()

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

        with open('post.json', 'w') as fp:
            fp.write(json.dumps(posts))

        with open('coms.json', 'w') as fc:
            fc.write(json.dumps(coms))

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
                                'comment': self.remove_non_utf8_characters(cmt["text"]),
                                'published_at': date.strftime("%d/%m/%Y"),
                                'likes': cmt["comment_like_count"],
                                'author': cmt["user"]["full_name"],
                                'author_page_url': ''
                            })
                    except Exception as e:
                        print(e)
                        pass

                try:
                    if 'caption' in post.keys() and 'comments' in post.keys() and 'caption' in post['comments'].keys():
                        published_at = datetime.fromtimestamp(
                            post["comments"]["caption"]["created_at"])
                        published_at > (datetime.now() - timedelta(days=365)) and post["owner"]["full_name"] and post["caption"]["text"] and self.posts.append({
                            "post_url": '',
                            "author": post["owner"]["full_name"],
                            "publishedAt": published_at.strftime("%d/%m/%Y"),
                            "description": self.remove_non_utf8_characters(post["caption"]["text"]),
                            "reaction": post["like_count"],
                            "comments": len(comment_values),
                            "shares": 0,
                            "hashtag": "",
                            "comment_values": comment_values
                        })

                        print({
                            "post_url": '',
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

            print(self.page_data)

        except Exception as e:
            print(e)
            pass

    def switch_acount(self) -> None:
        pass

    def execute(self) -> None:
        progress = ChargingBar('Preparing ', max=3)
        self.set_current_credential(0)
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


class InstagramProfileScraper(Scraping):

    def __init__(self, items: list = []) -> None:
        super().__init__(items)
        self.set_credentials('instagram')

        self.xhr_page = {}
        self.xhr_comments = {}
        self.last_date = datetime.now()
        self.name = ""

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False, args=['--start-maximized'])
        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()
        self.post_index = 0
        self.open_post = False

    def goto_login(self) -> None:
        self.page.goto(
            "https://www.instagram.com/accounts/login/", timeout=30000)
        self.page.wait_for_timeout(30000)

    def resolve_loginform(self) -> None:
        self.fill_loginform()

    def fill_loginform(self) -> None:
        print("\t ==> filling login form")
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
            if 'query' in response.url:
                try:
                    if response.json()['data']['user']:
                        self.xhr_page = response.json()['data']['user']
                except KeyError:
                    pass
            if 'comments/' in response.url:
                try:
                    self.xhr_comments = response.json()
                except Exception as e:
                    print(e)
                    pass

    def goto_insta_page(self) -> None:
        print(f"\t  ==> go to {self.url}")
        self.page.on("response", self.intercept_response)
        self.page.goto(self.url, timeout=50000)
        self.page.wait_for_timeout(6000)
        time.sleep(5)

    def get_likes_of_current_article(self) -> int:
        article = self.page.locator("//article[@role='presentation']")
        try:
            like = article.locator("span.html-span.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1hl2dhg.x16tdsg8.x1vvkbs").inner_text()
            print(f"like {like}")
            return int(like)
        except:
            return 0
        
    def get_date_of_current_article(self) -> str:
        try:
            date = datetime.fromisoformat(self.driver.find_element(By.XPATH, "//time[@class='x1p4m5qa']").get_attribute('datetime')).strftime("%Y-%m-%d")
            return date
        except:
            print(f"Failed to transform date")
    
    def open_post(self) -> None:
        print("\t ==> opening post")
        posts = self.page.locator("div._ac7v.xzboxd6.xras4av.xgc1b0m a.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz._a6hd").all()
        try:
            posts[0].click()
        except:
            print('no post found')
        time.sleep(3)

    def go_next(self) -> None:
        btns = self.page.locator("div.x1n2onr6.xzkaem6").locator("button._abl-").all()
        for btn in btns:
            if len(btn.locator('svg').all()) > 0:
                for svg in btn.locator('svg').all():
                    if svg.get_attribute('aria-label') == "Suivant" or svg.get_attribute('aria-label') == "Next":
                        btn.click()
                        time.sleep(3)
                        break
    
    def extract_page_profile(self) -> None:
        print("\t ==> extracting profile data")

        self.name = nested_lookup(key='full_name', document=self.xhr_page)[0]
        name = re.sub(r'[^a-zA-Z0-9\s]', '', self.name).replace(' ', '_')
        try:
            self.page_data = {
            "followers": nested_lookup(key='follower_count', document=self.xhr_page)[0],
            "likes": 0,
            "source": "instagram",
            "establishment": self.establishment,
            "name": f"instagram_{name}",
            }
        except:
            pass
        print(f"profile {self.page_data}")

    def extract_current_article_data(self) -> dict:
        print("\t ==> extracting post")
        if self.xhr_comments:
            post = {}
            try:
                post_data = []
                try:
                    post_data = self.xhr_comments['caption']
                except:
                    print("no post data item")
                comments = self.xhr_comments['comments']
                post['post_url'] = self.page.url
                if post_data:
                    post['author'] = post_data['user']['full_name']
                    post['description'] = post_data['text']
                    # post['publishedAt'] = datetime.fromtimestamp(post_data['created_at']).strftime("%d/%m/%Y")
                    post['publishedAt'] = datetime.fromtimestamp(post_data['created_at']).strftime("%Y-%m-%d")
                else:
                    post['author'] = self.name
                    post['description'] = ""
                    post['publishedAt'] = self.get_date_of_current_article()
                post['reaction'] = self.get_likes_of_current_article()
                post["shares"] = 0
                post["hashtag"] = ""
                post["comment_values"] = []

                for comment in comments:
                    post["comment_values"].append({
                        "author": comment['user']['full_name'],
                        "comment": comment['text'],
                        "author_page_url": f"https://www.instagram.com/{comment['user']['username']}/",
                        "likes": comment['comment_like_count'],
                        # "published_at": datetime.fromtimestamp(comment['created_at']).strftime('%d/%m/%Y')
                        "published_at": datetime.fromtimestamp(comment['created_at']).strftime('%Y-%m-%d')
                    })

                post['comments'] = len(post['comment_values'])
                self.last_date = datetime.fromtimestamp(post_data['created_at'])
                print(post)
                return post
            except:
                return {}
    
    def check_page_data(self) -> None:
        while True:
            time.sleep(2)
            self.extract_page_profile()
            if self.page_data:
                break
            else:
                self.page.reload()
                time.sleep(2)

    def extract(self) -> None:
        print("\t ==> extraction")
        time.sleep(2)
        self.extract_page_profile()
        posts = self.page.locator("div._ac7v.xzboxd6.xras4av.xgc1b0m a.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz._a6hd").all()
        try:
            posts[0].click()
        except:
            print('no post found')
        while True:
            post = self.extract_current_article_data()
            if post:
                self.posts.append(post)
            if self.last_date < (datetime.now() - timedelta(days=60)):
                break
            self.go_next()

    def execute(self):
        # self.set_credentials(0)
        self.goto_login()
        self.fill_loginform()
        output_files = []
        for item in self.items:
            print(f" ==> item {item}")
            self.set_item(item)
            self.goto_insta_page()
            self.check_page_data()
            time.sleep(2)
            self.extract()
            output_files.append(self.save())
            print(" | Saved")
            self.page_data.clear()
        return output_files
