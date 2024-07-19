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

        self.xhr_page = {}
        self.xhr_comments = {}
        self.last_date = datetime.now()

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
            return like
        except:
            return 0
    
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
        try:
            self.page_data = {
            "followers": nested_lookup(key='follower_count', document=self.xhr_page)[0],
            "like": 0,
            "source": "instagram",
            "establishment": self.establishment,
            "name": f"instagram_{nested_lookup(key='full_name', document=self.xhr_page)[0]}",
            }
        except:
            pass
        print(f"profile {self.page_data}")

    def extract_current_article_data(self) -> dict:
        print("\t ==> extracting post")
        if self.xhr_comments:
            post = {}
            post_data = self.xhr_comments['caption']
            comments = self.xhr_comments['comments']
            post['publishedAt'] = datetime.fromtimestamp(post_data['created_at']).strftime("%d/%m/%Y")
            post['author'] = post_data['user']['full_name']
            post['description'] = post_data['text']
            post['reaction'] = self.get_likes_of_current_article()
            post["shares"] = 0
            post["hashtag"] = ""
            post["comment_values"] = []

            for comment in comments:
                post["comment_values"].append({
                    "comment": comment['text'],
                    "published_at": datetime.fromtimestamp(comment['created_at']).strftime('%d/%m/%Y'),
                    "likes": comment['comment_like_count'],
                    "author": comment['user']['full_name'],
                    "author_page_url": f"https://www.instagram.com/{comment['user']['username']}/"
                })

            self.last_date = datetime.fromtimestamp(post_data['created_at'])
            print(post)
            return post
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
            if self.last_date < (datetime.now() - timedelta(days=30)):
                break
            self.go_next()

    def execute(self):
        # self.set_credentials(0)
        self.goto_login()
        self.fill_loginform()
        for item in self.items:
            print(f" ==> item {item}")
            self.set_item(item)
            self.goto_insta_page()
            self.check_page_data()
            time.sleep(2)
            # self.open_post()
            self.extract()
            self.page_data.clear()



if __name__ == '__main__':

    data = [
            {'id': 206, 'caption': '', 'section': 'FOLLOW US', 'establishment_name': 'AMSB', 'establishment_id': 63, 'idprovider': 15, 'category': 'Social', 'source': 'Instagram', 'url': 'https://www.instagram.com/amsbofficiel', 'language': 'fr', 'last_review_date': None}, 
            {'id': 221, 'caption': '', 'section': 'FOLLOW US', 'establishment_name': 'SOC Rugby', 'establishment_id': 69, 'idprovider': 15, 'category': 'Social', 'source': 'Instagram', 'url': 'https://www.instagram.com/soc.rugby_officiel', 'language': 'fr', 'last_review_date': None}, 
            {'id': 189, 'caption': None, 'section': None, 'establishment_name': 'Mondovélo Chambéry', 'establishment_id': 54, 'idprovider': 15, 'category': 'Social', 'source': 'Instagram', 'url': 'https://www.instagram.com/mondovelochambery/', 'language': 'fr', 'last_review_date': None}, 
            {'id': 188, 'caption': None, 'section': None, 'establishment_name': 'Degrif Sport Aix-les-Bains', 'establishment_id': 55, 'idprovider': 15, 'category': 'Social', 'source': 'Instagram', 'url': 'https://www.instagram.com/degrif_sport_aixlesbains', 'language': 'fr', 'last_review_date': None}, 
            {'id': 175, 'caption': None, 'section': None, 'establishment_name': 'Sport2000 France', 'establishment_id': 52, 'idprovider': 15, 'category': 'Social', 'source': 'Instagram', 'url': 'https://www.instagram.com/sport2000fr', 'language': 'fr', 'last_review_date': None}, 
            {'id': 158, 'caption': None, 'section': None, 'establishment_name': 'Team Chambé', 'establishment_id': 49, 'idprovider': 15, 'category': 'Social', 'source': 'Instagram', 'url': 'https://www.instagram.com/teamchambe', 'language': 'fr', 'last_review_date': None}, 
            {'id': 155, 'caption': None, 'section': None, 'establishment_name': 'Domaine de Bonelli', 'establishment_id': 48, 'idprovider': 15, 'category': 'Social', 'source': 'Instagram', 'url': 'https://www.instagram.com/domainedebonelli', 'language': 'fr', 'last_review_date': None}, 
            {'id': 150, 'caption': None, 'section': None, 'establishment_name': 'Hôtel du Golfe Ajaccio', 'establishment_id': 47, 'idprovider': 15, 'category': 'Social', 'source': 'Instagram', 'url': 'https://www.instagram.com/hoteldugolfeajaccio', 'language': 'fr', 'last_review_date': None}, 
            {'id': 141, 'caption': None, 'section': 'FOLLOW US', 'establishment_name': 'Dolce Notte', 'establishment_id': 46, 'idprovider': 15, 'category': 'Social', 'source': 'Instagram', 'url': 'https://www.instagram.com/hoteldolcenotte', 'language': 'fr', 'last_review_date': None}, 
            {'id': 129, 'caption': None, 'section': 'FOLLOW US', 'establishment_name': "Le Carre d'As", 'establishment_id': 44, 'idprovider': 15, 'category': 'Social', 'source': 'Instagram', 'url': 'https://www.instagram.com/carredas73', 'language': 'fr', 'last_review_date': None}, 
            {'id': 102, 'caption': None, 'section': None, 'establishment_name': 'Le Château de Candie', 'establishment_id': 4, 'idprovider': 15, 'category': 'Social', 'source': 'Instagram', 'url': 'https://www.instagram.com/chateaudecandie', 'language': 'fr', 'last_review_date': None}, 
            {'id': 93, 'caption': None, 'section': None, 'establishment_name': 'Hotel Chamartín The One', 'establishment_id': 28, 'idprovider': 15, 'category': 'Social', 'source': 'Instagram', 'url': 'https://www.instagram.com/chamartin_theone', 'language': 'es', 'last_review_date': None}, 
            {'id': 89, 'caption': None, 'section': 'FOLLOW US', 'establishment_name': 'Hotel Antequera Hills', 'establishment_id': 27, 'idprovider': 15, 'category': 'Social', 'source': 'Instagram', 'url': 'https://www.instagram.com/hotelantequerahills', 'language': 'es', 'last_review_date': None}, 
            {'id': 46, 'caption': None, 'section': None, 'establishment_name': 'Le Lido', 'establishment_id': 5, 'idprovider': 15, 'category': 'Social', 'source': 'Instagram', 'url': 'https://www.instagram.com/lidolacdubourget', 'language': 'fr', 'last_review_date': None}, 
            {'id': 42, 'caption': None, 'section': None, 'establishment_name': 'Office de Tourisme de Chamonix-Mont-Blanc', 'establishment_id': 12, 'idprovider': 15, 'category': 'Social', 'source': 'Instagram', 'url': 'https://www.instagram.com/chamonixmontblanc', 'language': 'fr', 'last_review_date': None}, 
            {'id': 24, 'caption': None, 'section': None, 'establishment_name': 'Madame Vacances', 'establishment_id': 7, 'idprovider': 15, 'category': 'Social', 'source': 'Instagram', 'url': 'https://www.instagram.com/madame_vacances', 'language': 'fr', 'last_review_date': None}
        ]


    i = InstagramProfileScraper(items=[data[2]])
    i.credentials = {
        "email": "",
        "password": "",
        "username": "domoina.sarobidy"
    }
    i.execute()