import json
from random import randint
from bs4 import BeautifulSoup
import time
from lingua import Language, LanguageDetectorBuilder
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver.support import expected_conditions as EC
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
        self.set_credentials('facebook')

        self.post_detail = []
        self.last_date = ""
        self.page_data = {}

        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_argument('--incognito')
        self.chrome_options.add_argument('--lang=en')
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.static_folder_path = f"{os.environ.get('STATIC_FOLDER')}/facebook"

    def stop(self):
        pass

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

    def create_logfile(self, logfile_name: str) -> None:
        self.filename = f"{self.static_folder_path}/{logfile_name}.json"
        if not Path(self.filename).exists():
            with open(self.filename, 'w') as openfile:
                pass

    def load_history(self) -> None:
        if not Path(self.filename).exists():
            with open(self.filename, 'w') as openfile:
                pass

    def set_history(self, key: str, value: any) -> None:
        pass

    def goto_login(self) -> None:
        self.driver.get("https://www.facebook.com/")
        WebDriverWait(self.driver, 10000)
        time.sleep(randint(5, 10))


    def fomate_date(self, date:str) -> str:
        date = date.split('-')[0].strip()
        if len(date.split(' ')) <= 2:
            return datetime.strptime(date, "%B %d")
        elif len(date.split(' ')) > 2 and ',' in date:
            date = date[0: date.index(',') + 6].replace(',' , '')
            print(date)
            return datetime.strptime(date, "%B %d %Y")
        
    def get_all_detail_links(self):
        soupe = BeautifulSoup(self.driver.page_source, 'lxml')
        links = soupe.find_all('a', {'class':'x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1sur9pj xkrqix3 xi81zsa xo1l8bm'}, href=True)
        print(len(links))
        for link in links:
            ak = link['href']
            if ak and '/posts/' in ak:
                self.post_detail.append(ak)
        self.post_detail = list(set(self.post_detail))

    def resolve_login_forme(self) -> None:
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

    def goto_fb_page(self) -> None:
        self.driver.get(self.url)
        time.sleep(randint(5, 10))
        

    def load_page_content(self) -> None:
        post_loaded = False
        while not post_loaded:
            post_container = self.driver.find_element(By.CSS_SELECTOR, "div.x9f619.x1n2onr6.x1ja2u2z.xeuugli.xs83m0k.x1xmf6yo.x1emribx.x1e56ztr.x1i64zmx.xjl7jj.x19h7ccj.xu9j1y6.x7ep2pv")
            dates_link = post_container.find_elements(By.CSS_SELECTOR, "span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.x4zkp8e.x676frb.x1pg5gke.x1sibtaa.xo1l8bm.xi81zsa.x1yc453h")
            if dates_link:
                dates_link[-1].find_element(By.CSS_SELECTOR, 'span.x4k7w5x.x1h91t0o.x1h9r5lt.x1jfb8zj.xv2umb2.x1beo9mf.xaigb6o.x12ejxvf.x3igimt.xarpa2k.xedcshv.x1lytzrv.x1t2pt76.x7ja8zs.x1qrby5j').location_once_scrolled_into_view
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)
                time.sleep(1)
                last_date = pytesseract.image_to_string(Image.open(io.BytesIO(dates_link[-1].screenshot_as_png))).replace('\n', '')
                last_date = self.fomate_date(last_date)
                if last_date < (datetime.now() - timedelta(days=365)):
                    self.get_all_detail_links()
                    print(f"{len(self.post_detail)} post links extracted")
                    self.page_data['post_links'] = self.post_detail
                    post_loaded = True
                else:
                    pass
            else:
                print('no post found or detail link selector changed')
            
            self.get_all_detail_links()

            for i in range(3):
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)


    def extract_page_data(self) -> None:
        soupe = BeautifulSoup(self.page.content(), 'lxml')
        page_name = soupe.find('div', {'class': "x1e56ztr x1xmf6yo"}).text \
            if soupe.find('div', {'class': "x1e56ztr x1xmf6yo"}) else ''
        page_likes = soupe.find_all('a', {'class': "x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1s688f"})[0].text.strip() \
            if soupe.find_all('a', {'class': "x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1s688f"}) else 0

        page_likes = self.format_string_number(page_likes)
        print(page_likes)

        page_followers = soupe.find_all('a', {'class': "x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1s688f"})[1].text.strip() \
            if soupe.find_all('a', {'class': "x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1s688f"}) else 0

        page_followers = self.format_string_number(page_followers)

        self.page_data = {
            'name': f"fb_{page_name}",
            'likes': int(''.join(filter(str.isdigit, page_likes))),
            'followers': int(''.join(filter(str.isdigit, page_followers))),
            'source': 'facebook',
            'establishment': self.establishment,
            'posts': len(self.posts)
        }

    def save_content(self) -> None:
        with open(self.filename, 'w') as openfile:
            openfile.write(json.dumps(self.page_data))

    def switch_acount(self) -> None:
        pass

    def execute(self) -> None:
        self.set_current_credential(1)
        print(" | Open login page")
        self.goto_login()
        self.resolve_login_forme()
        for item in self.items:
            try:
                self.set_item(item)
                print(" | Open page")
                self.goto_fb_page()
                print(" | Extract page data")
                self.extract_page_data()
                print(" | Load content page")
                self.load_page_content()
                self.create_logfile(self.page_data['name'])
                self.save_content()

            except:
                pass


class FacebookScraper(object):

    def __init__(self) -> None:
        self.file_index = ""
        self.items = {}
        self.page_data = {}
        self.credentials = {}
        self.static_folder_path = f"{os.environ.get('STATIC_FOLDER')}/facebook"

        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument(
            '--disable-blink-features=AutomationControlled')
        self.chrome_options.add_argument('--incognito')
        self.chrome_options.add_extension("C:/Users/Keller/Documents/Jobdev/scraping-v3/canvas_blocker_0_2_0_0.crx")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.maximize_window()

    def set_credentials(self, credentials:dict) -> None:
        self.credentials = credentials

    def open_page(self, url:str) -> None:
        print(f" ==> {url}")
        self.driver.get(url)
        WebDriverWait(self.driver, 10000)
        time.sleep(randint(5, 10))

    def set_index(self, new_index:int=0) -> None:
        self.file_index = new_index

    def load_files(self) -> None:
        files = os.listdir(f"{self.static_folder_path}/content/")
        with open(f"{self.static_folder_path}/content/{files[self.file_index]}", 'r') as openfile:
            self.items = json.load(openfile)
        print(f" {len(self.items['post_links'])} links loaded")

    def resolve_login_forme(self) -> None:
        self.driver.find_element(By.XPATH, "//input[@data-testid='royal_email']").click()
        time.sleep(randint(1, 3))
        self.driver.find_element(By.XPATH, "//input[@data-testid='royal_email']").send_keys(self.credentials['email'])
        time.sleep(randint(1, 3))
        self.driver.find_element(By.XPATH, "//input[@data-testid='royal_pass']").click()
        time.sleep(randint(1, 3))
        self.driver.find_element(By.XPATH, "//input[@data-testid='royal_pass']").send_keys(self.credentials['password'])
        time.sleep(randint(1, 3))
        self.driver.find_element(By.XPATH, "//button[@data-testid='royal_login_button']").click()
        time.sleep(randint(10, 20))

    def goto_fb_page(self) -> None:
        self.driver.get(self.items['page_url'])
        time.sleep(randint(5, 10))

    def parse_int(self, text:str) -> int:
        likes = text.strip().lower().replace('.', '').replace(',', '').replace('\xa0', '').replace(' likes', '').replace("j’aime", '').replace(' followers', '').replace("abonnées", '')
        print(text)
        if 'k' in likes:
            likes = int(float(likes.replace('k', '')) * 1000)
            return likes
        if 'm' in likes:
            likes = int(float(likes.replace('m', '')) * 1000000)
            return likes
        likes = int(float(likes))
        return likes
        

    def extract_page_data(self) -> None:
        soupe = BeautifulSoup(self.driver.page_source, 'lxml')
        header = soupe.find('div', {'class':'x78zum5 x15sbx0n x5oxk1f x1jxijyj xym1h4x xuy2c7u x1ltux0g xc9uqle'})
        followers_likes = header.find_all('a', {'class':'x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1sur9pj xkrqix3 xi81zsa x1s688f'})
        likes = self.parse_int(followers_likes[0].text)
        followers = self.parse_int(followers_likes[1].text)
        name = header.find('h1', {'class':'html-h1 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1vvkbs x1heor9g x1qlqyl8 x1pd3egz x1a2a7pz'}).text.replace('\xa0', '')

        self.page_data = {
            'createdAt': datetime.now().strftime('%Y_%m_%d'),
            'followers': int(followers),
            "hasStat": "1",
            'name': f"{name}",
            'likes': int(likes),
            'source': 'facebook',
            'establishment': self.items['establishement'],
            'posts': []
        }

        print(self.page_data)

    def format_date_en(self, date_text:str) -> datetime | str:
        date_text = date_text.split('-')[0].strip().lower().split('at')[0].strip()
        print(date_text)
        if date_text:
            if date_text[0].isdigit() or 'ago' in date_text:
                if len(date_text.split(' ')) == 1:
                    if 's' in date_text or 'm' in date_text:
                        return (datetime.now() - timedelta(seconds=int(date_text.split('s')[0].split('m')[0]))).strftime('%d/%m/%Y')
                    if 'h' in date_text:
                        return (datetime.now() - timedelta(hours=int(date_text.split('h')[0])))
                else:
                    if 'a day ago' in date_text:
                        return (datetime.now() - timedelta(hours=24))
                    if 'hours ago' in date_text:
                        return (datetime.now() - timedelta(hours=int(date_text.split('hours ago')[0].strip())))
                    if 'days ago' in date_text:
                        return (datetime.now() - timedelta(days=int(date_text.split('days ago')[0].strip())))
            else:
                if 'yesterday' in date_text:
                    return (datetime.now() - timedelta(days=1))
                if any(chr.isdigit() for chr in date_text):
                    date_non = ''
                    for i in date_text:
                        if i.isdigit():
                            if date_text[date_text.index(i)-1] != ' ':
                                date_text = list(date_text)
                                print(date_text)
                                date_text.insert(date_text.index(i), ' ')
                                date_non = ''.join(date_text)
                                break
                            else:
                                date_non = date_text
                                break
                    if len(date_non.split(' ')) == 2:
                        date_non += f" {datetime.now().year}"
                        return datetime.strptime(date_non, "%B %d %Y")  
                    if len(date_non.split(' ')) > 2 and ',' in date_non:
                        date = date_non[0: date_non.index(',') + 6].replace(',' , '')
                        return datetime.strptime(date, "%B %d %Y")

    def get_post_date(self) -> object | None:
        try:
            date_tag = self.driver.find_element(By.CSS_SELECTOR, "div.html-div.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1q0g3np")
            # date_tag = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[2]/div/div[2]/span/span")
            date_tag.location_once_scrolled_into_view
            self.driver.execute_script("window.scrollBy(0, -150);")
            date = pytesseract.image_to_string(Image.open(io.BytesIO(date_tag.screenshot_as_png))).replace('\n', '')
            if date:
                with open('dates.json', 'a') as openfile:
                    openfile.write(f"{date} \n")
                date = self.format_date(date)
                return date
            else:
                print(f"date format incorrect {date}")
        except:
            print('date tag not found')

    def load_comments(self) -> None:
        try:
            like_icon = self.driver.find_element(By.CSS_SELECTOR, "span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.xudqn12.x3x7a5m.x1f6kntn.xvq8zen.x1s688f.xi81zsa")
            like_icon.location_once_scrolled_into_view
            time.sleep(randint(1, 2))
            self.driver.execute_script("window.scrollBy(0, -150);")
            time.sleep(randint(1, 2))
            comment_list_filter = self.driver.find_element(By.CSS_SELECTOR, "div.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1o1ewxj.x3x9cwd.x1e5q0jg.x13rtm0m.x1n2onr6.x87ps6o.x1lku1pv.x1a2a7pz")
            comment_list_filter.click()
            time.sleep(randint(1, 3))
            comment_filters = self.driver.find_elements(By.CSS_SELECTOR, 'span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.xudqn12.x3x7a5m.x1f6kntn.xvq8zen.xk50ysn.xzsf02u.x1yc453h')
            comment_filters[-1].click()
            time.sleep(randint(3, 5))
            view_all_comments = self.driver.find_elements(By.CSS_SELECTOR, "span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.xudqn12.x3x7a5m.x1f6kntn.xvq8zen.x1s688f.xi81zsa")
            while 'more'in view_all_comments[-1].text:
                view_all_comments[-1].location_once_scrolled_into_view
                time.sleep(randint(1, 2))
                print('ok')
                view_all_comments[-1].click()
                view_all_comments = self.driver.find_elements(By.CSS_SELECTOR, "span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.xudqn12.x3x7a5m.x1f6kntn.xvq8zen.x1s688f.xi81zsa")
        except:
            print("Is this post has no comment, if yes try to load manually all comments then press enter")
            pass

    def extract_post(self, date:str) -> None:
        print('extraction')
        def format_comment_date(date:str) -> str | None:
            if 'd' in date:
                date_str = date.replace('d', '')
                date = (datetime.now() - timedelta(days=int(date_str))).strftime("%d/%m/%Y")
                return date
            if 'w' in date:
                date_str = date.replace('w', '')
                date = (datetime.now() - timedelta(days=(int(date_str)*7))).strftime("%d/%m/%Y")
                return date
            if 'y' in date:
                date_str = date.replace('y', '')
                date = (datetime.now() - timedelta(days=(int(date_str)*365))).strftime("%d/%m/%Y")
                return date
        post = {}
        soupe = BeautifulSoup(self.driver.page_source, 'lxml')
        post['author'] = soupe.find('h2', {'class':'html-h2 xe8uvvx x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1vvkbs x1heor9g x1qlqyl8 x1pd3egz x1a2a7pz x1gslohp x1yc453h'}).text
        try:
            post['description'] = soupe.find('span', {'class':'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x1f6kntn xvq8zen xo1l8bm xzsf02u x1yc453h'}).text
        except:
            post['description'] = ''
        post["hashtag"] = ""
        post["publishedAt"] = date
        try:
            post["reactions"] = int(soupe.find('span', {'class':'xt0b8zv x2bj2ny xrbpyxo xl423tq'}).text)
        except:
            post["reactions"] = 0
        try:
            post_data = soupe.find_all('span', {'class':'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x1f6kntn xvq8zen xo1l8bm xi81zsa'})
            if len(post_data) == 3:
                post["shares"] = post_data[-1].text.split(' ')[0]
            else:
                post["shares"] = 0
        except:
            post["shares"] = 0

        post['url'] = self.driver.current_url
        

        comment_section = soupe.find('div', {'class':'x1pi30zi x1swvt13 x1n2onr6'})
        comments = comment_section.find_all('div', {'role':'article', 'class':'x1n2onr6 x1swvt13 x1iorvi4 x78zum5 x1q0g3np x1a2a7pz'})
        comments_data = []
        for comment in comments:
            c = {}
            c['author'] = comment.find('span', {'class':'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x676frb x1pg5gke x1sibtaa x1s688f xzsf02u'}).text
            c['puplished_at'] = format_comment_date(comment.find('span', {'class':'html-span xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1hl2dhg x16tdsg8 x1vvkbs'}).text)
            
            try:
                c['text'] = comment.find('div', {'class':'xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs'}).text
            except:
                c['text'] = ''
            try:
                c['reaction'] = len(comment.find('div', {'class':'x6s0dn4 x78zum5 x15zctf7 x1e558r4'}).find_all('span'))
            except:
                c['reaction'] = 0
            comments_data.append(c)

        post["comment_values"] = comments_data
        post["comments"] = len(comments_data)
        print(post)
        self.page_data['posts'].append(post)

    def save_data(self):
        with open(f"{self.static_folder_path}/data/{self.page_data['name']}.json", "w", encoding='utf-8') as openfile:
            openfile.write(json.dumps(self.page_data, indent=4))

    def execute(self) -> None:
        print(' | Opening page')
        self.open_page("https://www.facebook.com/")
        print(' | Load content')
        self.load_files()
        print(' | Login In')
        self.resolve_login_forme()
        print(' | Go to fb page')
        self.goto_fb_page()
        print(' | Extract page data')
        self.extract_page_data()
        for i in range(len(self.items['post_links'])):
            print(i)
            self.open_page(self.items['post_links'][i])
            if "/posts/" not in self.driver.current_url:
                continue
            post_date = self.get_post_date()
            if not post_date:
                continue
            print(' | Loading all comments')
            self.load_comments()
            print(' | Extracting comments')
            self.extract_post(post_date)
            print(" | Saving data")
            self.save_data()

credentials = {
    "email": "rakotonomenjanaharymario9@gmail.com",
    "password": "_kreBY!u4&jxbiX"
}

f = FacebookScraper()
f.set_credentials(credentials)
f.set_index(2)
f.execute()

    
