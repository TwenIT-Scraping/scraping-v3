import json
from random import randint
from bs4 import BeautifulSoup
import time
from lingua import Language, LanguageDetectorBuilder
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pytesseract
from datetime import datetime, timedelta
from PIL import Image
from pathlib import Path
import base64
import io
import os
from scraping import Scraping


pytesseract.pytesseract.tesseract_cmd = "C:/Program Files (x86)/pytesseract/tesseract.exe"



class BaseFacebookScraper(Scraping):

    def __init__(self, items: list = []) -> None:
        super().__init__(items)

        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument(
            '--disable-blink-features=AutomationControlled')
        self.chrome_options.add_argument('--incognito')
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.maximize_window()
        self.static_folder_path = f"{os.environ.get('STATIC_FOLDER')}/facebook"
        self.credentials = {
            "username": "",
            "phone":"",
            "password":""
        }

    def detect_lang(self, text: str) -> str:
        if text:
            lang_code = {
                'Language.ENGLISH': 'en',
                'Language.GERMAN': 'de',
                'Language.SPANISH': 'es',
                'Language.FRENCH': 'fr',
            }

        languages = [Language.ENGLISH, Language.FRENCH,
                     Language.GERMAN, Language.SPANISH]
        detector = LanguageDetectorBuilder.from_languages(*languages).build()
        try:
            return lang_code[f"{detector.detect_language_of(text)}"]
        except:
            return ''
        
    def goto_login(self) -> None:
        self.driver.get("https://www.facebook.com/")
        WebDriverWait(self.driver, 10000)
        time.sleep(randint(5, 10))

    def resolve_login_form(self) -> None:
        print(" Login In")
        self.driver.find_element(By.XPATH, "//input[@data-testid='royal_email']").click()
        time.sleep(randint(1, 3))
        self.driver.find_element(By.XPATH, "//input[@data-testid='royal_email']").send_keys(self.credentials['phone'])
        time.sleep(randint(1, 3))
        self.driver.find_element(By.XPATH, "//input[@data-testid='royal_pass']").click()
        time.sleep(randint(1, 3))
        self.driver.find_element(By.XPATH, "//input[@data-testid='royal_pass']").send_keys(self.credentials['password'])
        time.sleep(randint(1, 3))
        self.driver.find_element(By.XPATH, "//button[@data-testid='royal_login_button']").click()
        time.sleep(randint(10, 20))

    def format_date(self, date_string:str) -> object:
        if ' at' in date_string:
            date_string = date_string.split(' at')[0]
        date = date_string.split('-')[0]
        if date[-1] == ' ':
            date = date[:-1]
        if len(date.split(' ')) <= 2:
            date += f" {datetime.now().year}"
            date = datetime.strptime(date, "%B %d %Y").strftime("%d/%m/%Y")
            print(date)
            return date
        elif len(date.split(' ')) > 2 and ',' in date:
            date = date[0: date.index(',') + 6].replace(',' , '')
            print(date)
            return datetime.strptime(date, "%B %d %Y").strftime("%d/%m/%Y")
        else:
            return date

    def save_post(self):
        print(len(self.page_data['post_links']))
        pass
        
    def execute(self) -> None:
        self.goto_login()
        self.resolve_login_form()

class FacebookProfileScraper(BaseFacebookScraper):

    def __init__(self, items: list = []) -> None:
        super().__init__(items)
        self.last_index = 0
        self.current_date = datetime.now()
        self.new_posts_number = 0
        self.current_posts_number = 0
        self.posts_loaded = False

    def goto_fb_page(self) -> None:
        print(f" ==>go to {self.url}")
        self.driver.get(self.url)
        time.sleep(randint(5, 10))

    def extract_page_data(self) -> None:
        print(" ==> extracting page data")
        def format_string_to_number(text:str) -> int | None:
            numb = text.replace(' followers', '').replace(' likes', '').replace('K', "000").replace('M', '000000').replace('.', '').replace(',', '')
            try:
                numb = int(numb)
                return numb
            except:
                print(f" {numb} cannot be formated to int")

        soupe = BeautifulSoup(self.driver.page_source, 'lxml')
        header = soupe.find('div', {'class':'x78zum5 x15sbx0n x5oxk1f x1jxijyj xym1h4x xuy2c7u x1ltux0g xc9uqle'})
        page_name = header.find('h1', {'class':'html-h1 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1vvkbs x1heor9g x1qlqyl8 x1pd3egz x1a2a7pz'}).text.replace('\xa0', '')
        followers_likes = header.find_all('a', {'class':'x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1sur9pj xkrqix3 xi81zsa x1s688f'})
        page_likes = format_string_to_number(followers_likes[0].text)
        page_followers = format_string_to_number(followers_likes[1].text)

        self.page_data = {
            'name': f"fb_{page_name}",
            'likes': page_likes,
            'followers': page_followers,
            'source': 'facebook',
            'establishment': self.establishment,
            'post_links': [],
            'posts': []
        }
    
    def scroll_little_up(self, range_value:int):
        for i in range(range_value):
            self.driver.execute_script("window.scrollBy(0, 150);")
            time.sleep(1)
        time.sleep(randint(2, 5))

    def scroll_little_down(self, range_value:int):
        for i in range(range_value):
            self.driver.execute_script("window.scrollBy(0, -150);")
            time.sleep(1)
        time.sleep(randint(2, 5))

    def extract_date(self, element:object) -> object:
        date = pytesseract.image_to_string(Image.open(io.BytesIO(element.screenshot_as_png))).replace('\n', '')
        # date =  self.format_date(date)
        print(f"date post {date}")
        with open("dates.json", 'a',encoding='utf-8') as openfile:
            openfile.write(f'"{date}",\n')
        return date

    def extract_post_data(self, post) -> None:
        print(" ==> extracting post")
        self.scroll_little_down(2)
        self.scroll_little_up(1)
        post.location_once_scrolled_into_view
        time.sleep(1)
        self.scroll_little_down(1)
        date_link = post.find_element(By.CSS_SELECTOR, "span.x4k7w5x.x1h91t0o.x1h9r5lt.x1jfb8zj.xv2umb2.x1beo9mf.xaigb6o.x12ejxvf.x3igimt.xarpa2k.xedcshv.x1lytzrv.x1t2pt76.x7ja8zs.x1qrby5j")
        date = self.extract_date(date_link)
        if type(date != datetime):
            print("date not correct format")
            
        else:
            self.last_date = date
            date = date.strftime("%d/%m/%Y")

        ActionChains(self.driver, duration=randint(1000, 1500)).move_to_element(date_link).perform()
        link = BeautifulSoup(date_link.get_attribute('innerHTML'), 'lxml').find('a', href=True)['href']
        print({'date_post':date, 'encrypted_link':link, 'perma_link':''})
        with open("posts.json", 'a',encoding='utf-8') as openfile:
            openfile.write(f"{json.dumps({'date_post':date, 'encrypted_link':link, 'perma_link':''}, indent=4)},\n")
        self.page_data['post_links'].append({'date_post':date, 'encrypted_link':link, 'perma_link':''})

    def get_posts(self) -> None:
        post_container = self.driver.find_element(By.CSS_SELECTOR, "div.x9f619.x1n2onr6.x1ja2u2z.xeuugli.xs83m0k.x1xmf6yo.x1emribx.x1e56ztr.x1i64zmx.xjl7jj.x19h7ccj.xu9j1y6.x7ep2pv")
        posts = post_container.find_elements(By.CSS_SELECTOR, "div.html-div.xe8uvvx.xdj266r.x11i5rnm.x1mh8g0r.x18d9i69.x1cy8zhl.x78zum5.x1q0g3np.xod5an3.x1pi30zi.x1swvt13.xz9dl7a")
        self.current_posts_number = len(posts)
        return posts

    def load_page_posts(self) -> None:

        def is_scroll_done(index:int) -> bool:
            if index < 3:
                return False
            if type(self.last_date == datetime) and self.last_date < datetime.now() - timedelta(days=365) or (self.new_posts_number == self.new_posts_number):
                return True

        menus = self.driver.find_elements(By.XPATH, "//div[@aria-label='Actions for this post']")
        menus[0].location_once_scrolled_into_view
        self.scroll_little_down(2)
        self.scroll_little_up(1)
        scroll_index = 0
        while not self.posts_loaded:
            posts = self.get_posts()
            if posts:
                try:
                    post = posts[self.last_index]
                    print(scroll_index)
                    print(self.last_index)
                    self.extract_post_data(post)
                    self.last_index += 1
                except IndexError:
                    self.scroll_little_down(4)
                    time.sleep(5)
                    self.scroll_little_up(4)
            time.sleep(randint(1, 3))
            if is_scroll_done(scroll_index):
                self.posts_loaded = True
            if scroll_index == 3:
                scroll_index = 0
            self.current_posts_number = self.new_posts_number
            
    def execute(self) -> None:
        super().execute()
        for item in self.items:
            self.set_item(item)
            self.goto_fb_page()
            self.extract_page_data()
            self.load_page_posts()

class FacebookPostScraper(BaseFacebookScraper):

    def __init__(self) -> None:
        super().__init__()

    def execute(self) -> None:
        super().execute()


if __name__ == '__main__':
    fb_page = [
        {'id': 215, 'caption': None, 'section': 'FOLLOW US', 'establishment_name': 'Madame Vacances', 'establishment_id': 46, 'idprovider': 28, 'category': 'Hashtag', 'source': 'Facebook hashtag', 'url': 'https://www.facebook.com/hashtag/dlkhgsd', 'language': 'FR', 'last_review_date': None}, 
        {'id': 213, 'caption': None, 'section': None, 'establishment_name': '28-50 Marylebone Lane', 'establishment_id': 45, 'idprovider': 28, 'category': 'Hashtag', 'source': 'Facebook hashtag', 'url': 'https://www.facebook.com/hashtag/dlkhgsd', 'language': 'FR', 'last_review_date': None}, 
        {'id': 181, 'caption': None, 'section': None, 'establishment_name': 'Le Lido', 'establishment_id': 41, 'idprovider': 28, 'category': 'Hashtag', 'source': 'Facebook hashtag', 'url': 'https://www.facebook.com/hashtag/test01', 'language': 'FR', 'last_review_date': None}, 
        {'id': 180, 'caption': None, 'section': None, 'establishment_name': 'Le Lido', 'establishment_id': 41, 'idprovider': 28, 'category': 'Hashtag', 'source': 'Facebook hashtag', 'url': 'https://www.facebook.com/hashtag/test', 'language': 'FR', 'last_review_date': None}, 
        {'id': 154, 'caption': None, 'section': None, 'establishment_name': 'Le Lido', 'establishment_id': 41, 'idprovider': 28, 'category': 'Hashtag', 'source': 'Facebook hashtag', 'url': 'https://www.facebook.com/hashtag/test', 'language': 'FR', 'last_review_date': None}, 
        {'id': 149, 'caption': None, 'section': None, 'establishment_name': 'Madame Vacances', 'establishment_id': 46, 'idprovider': 28, 'category': 'Hashtag', 'source': 'Facebook hashtag', 'url': 'https://www.facebook.com/hashtag/madamevacances', 'language': 'FR', 'last_review_date': None}, 
        {'id': 148, 'caption': None, 'section': None, 'establishment_name': 'Les Chalets du Berger', 'establishment_id': 3, 'idprovider': 28, 'category': 'Hashtag', 'source': 'Facebook hashtag', 'url': 'https://www.facebook.com/hashtag/madamevacances', 'language': 'FR', 'last_review_date': None}, 
        {'id': 146, 'caption': None, 'section': None, 'establishment_name': 'MV Transport', 'establishment_id': 47, 'idprovider': 28, 'category': 'Hashtag', 'source': 'Facebook hashtag', 'url': 'https://www.facebook.com/hashtag/work', 'language': 'FR', 'last_review_date': None}, 
        {'id': 144, 'caption': None, 'section': None, 'establishment_name': 'MV Transport', 'establishment_id': 47, 'idprovider': 28, 'category': 'Hashtag', 'source': 'Facebook hashtag', 'url': 'https://www.facebook.com/hashtag/test', 'language': 'FR', 'last_review_date': None}, 
        {'id': 135, 'caption': None, 'section': None, 'establishment_name': 'Les Chalets du Berger', 'establishment_id': 3, 'idprovider': 28, 'category': 'Hashtag', 'source': 'Facebook hashtag', 'url': 'https://www.facebook.com/hashtag/leschaletsduberger', 'language': 'FR', 'last_review_date': None}, 
        {'id': 133, 'caption': None, 'section': None, 'establishment_name': 'Madame Vacances', 'establishment_id': 46, 'idprovider': 28, 'category': 'Hashtag', 'source': 'Facebook hashtag', 'url': 'https://www.facebook.com/hashtag/Madamevacances', 'language': 'FR', 'last_review_date': None}, 
        {'id': 123, 'caption': None, 'section': None, 'establishment_name': 'Madame Vacances', 'establishment_id': 46, 'idprovider': 28, 'category': 'Hashtag', 'source': 'Facebook hashtag', 'url': 'https://www.facebook.com/hashtag/madamevacances', 'language': 'FR', 'last_review_date': None}
        ]
    f = FacebookProfileScraper(items=fb_page)
    f.execute()
