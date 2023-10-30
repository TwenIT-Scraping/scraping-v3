from playwright.sync_api import sync_playwright
from nested_lookup import nested_lookup
from random import randint
from datetime import datetime
import time
import json
from scraping import Scraping


class InstagramProfileScraper(Scraping):

    def __init__(self, items: list = []) -> None:
        print('==> initializing instagram scraper ...')
        super().__init__(items)
        self.set_credentials('instagram')

        self.hotel_page_urls = []
        self.xhr_calls = []
        self.data = []

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False, args=['--start-maximized'])
        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()

    def create_logfile(self, logfile_name: str) -> None:
        pass

    def load_history(self) -> None:
        pass

    def set_history(self, key: str, value: any) -> None:
        pass

    def resolve_loginform(self) -> None:
        print('==> resolving login form ...')
        self.fill_loginform()

    def goto_login(self) -> None:
        print('==> logging In ...')
        self.page.goto(
            "https://www.instagram.com/accounts/login/", timeout=30000)
        self.page.wait_for_timeout(60000)

    def log_out(self) -> None:
        print('==> logout ...')

    def fill_loginform(self) -> None:
        print('==> filling login form ...')
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
        print('==> submitted ...')
        self.page.wait_for_timeout(70000)

    def intercept_response(self, response) -> None:
        """capture all background requests and save them"""
        response_type = response.request.resource_type
        if response_type == "xhr":
            if 'web_profile_info' in response.url:
                self.xhr_calls = response.json()

    def goto_insta_page(self) -> None:
        self.page.on("response", self.intercept_response)
        self.page.goto(self.url, timeout=50000)
        self.page.wait_for_timeout(6000)
        time.sleep(3)

    def get_json_content(self, item: object, key: str) -> object:
        try:
            return item[key]
        except KeyError:
            return ''

    def extract_data(self) -> None:
        # with open("instadata.json", "w") as f:
        #     f.write(json.dumps(self.xhr_calls))

        all_posts = nested_lookup(
            key='edge_felix_video_timeline', document=self.xhr_calls)[0]['edges']

        for post in all_posts:

            try:
                self.posts.append({
                    "publishedAt": datetime.fromtimestamp(nested_lookup(key='taken_at_timestamp', document=post)[0]).strftime("%d/%m/%Y"),
                    "title": nested_lookup(key='text', document=post)[0],
                    "comments": nested_lookup(key='edge_media_to_comment', document=post)[0]['count'],
                    "likes": nested_lookup(key='edge_liked_by', document=post)[0]['count'],
                    "shares": "0"
                })
            except Exception as e:
                print("Exception 2")
                print(e)

        other_posts = nested_lookup(
            key='edge_owner_to_timeline_media', document=self.xhr_calls)[0]['edges']

        for other_post in other_posts:
            post_text = nested_lookup(
                key='node', document=other_post['node'])[0]
            self.posts.append({
                "publishedAt": datetime.fromtimestamp(nested_lookup(key='taken_at_timestamp', document=other_post)[0]).strftime("%d/%m/%Y"),
                "title": post_text['text'] if type(post_text) == str else '',
                "comments": nested_lookup(key='edge_media_to_comment', document=other_post)[0]['count'],
                "likes": nested_lookup(key='edge_liked_by', document=other_post)[0]['count'],
                "shares": "0"
            })

        self.page_data = {
            "followers": nested_lookup(key='edge_followed_by', document=self.xhr_calls)[0]['count'],
            "name": nested_lookup(key='full_name', document=self.xhr_calls)[0],
            "likes": 0,
            "source": "instagram",
            "establishement": f"/api/establishement/{self.establishment}",
            "posts": len(self.posts)
        }

    # def save(self) -> None:
    #     with open('./demo_insta.json', 'a') as openfile:
    #         openfile.write(json.dumps(self.data))
    #     self.data.clear()

    def switch_acount(self) -> None:
        pass

    def execute(self) -> None:
        self.set_current_credential(1)
        self.goto_login()
        self.fill_loginform()
        for item in self.items:
            print("Itérer ...")
            self.set_item(item)
            self.goto_insta_page()
            # self.load_page_content()
            self.extract_data()
            self.save()


# if __name__ == '__main__':
#     print("==> program is lauching ('_')")
#     t = InstagramProfileScraper()
#     t.goto_login()
#     t.fill_loginform()
#     t.load_hotel_pages()
#     for url in t.hotel_page_urls:
#         t.goto_insta_page(url)
#         t.extract_data()
#         t.save()
#     print("==> program finished ('_')")
