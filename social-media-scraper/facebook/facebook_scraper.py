from playwright.sync_api import sync_playwright
from random import randint
from bs4 import BeautifulSoup
import time
import json
import os


class FacebookProfileScraper(object):

    def __init__(self) -> None:
        print('==> initializing twitter scraper ...')
        self.credentials = {
            'email': 'sonalimampiemo@gmail.com',
            'password': 'Kl#23pol106',
            'phone_number': '0345861628'
        }
        self.hotel_page_urls = []
        self.xhr_calls = []
        self.data_container = []

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False, args=['--start-maximized'])
        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()

    def create_logfile(self, logfile_name:str) -> None:
        pass

    def load_history(self) -> None:
        pass

    def set_history(self, key:str, value:any) -> None:
        pass

    def resolve_loginform(self) -> None:
        print('==> resolving login form ...')
        self.fill_loginform()
        

    def goto_login(self) -> None:
        print('==> logging In ...')
        self.page.goto("https://www.facebook.com/")
        self.page.wait_for_timeout(30000)

    def log_out(self) -> None:
        print('==> logout ...')
        

    def fill_loginform(self) -> None:
        print('==> filling login form ...')
        self.page.wait_for_selector("[id='email']", timeout=5000)
        self.page.locator("[id='email']").click()
        time.sleep(.5)
        self.page.fill("[id='email']", self.credentials['email'])
        time.sleep(.3)
        self.page.locator("[id='pass']").click()
        time.sleep(.2)
        self.page.fill("[id='pass']", self.credentials['password'])
        time.sleep(.1)
        self.page.locator("[type='submit']").click()
        print('==> submitted ...')
        self.page.wait_for_timeout(4000)

    def load_hotel_pages(self) -> None:
        print('==> loading all hotels twitter pages ...')
        self.hotel_page_urls = [
            "https://www.facebook.com/lidolacdubourget/"
        ]
    
    def goto_fb_page(self, url:str) -> None:
        self.page.goto(url, timeout=80000)
        self.page.wait_for_timeout(10000)
        time.sleep(.5)

    def format_values(self, data:object) -> int:
        pass

    def scoll_down_page(self) -> None:
        for i in range(5):
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(20000)
            time.sleep(5)

    def get_post_count(self) -> str:
        soupe = BeautifulSoup(self.page.content(), 'lxml')
        current_post = soupe.find('div', {'class':"x9f619 x1n2onr6 x1ja2u2z xeuugli xs83m0k x1xmf6yo x1emribx x1e56ztr x1i64zmx xjl7jj x19h7ccj xu9j1y6 x7ep2pv"}).find_all('div', {'x1n2onr6 x1ja2u2z'})
        return len(current_post)

    def load_page_content(self) -> None:
        # self.scoll_down_page()
        self.extract_data()
        current_post = self.get_post_count() 
        new_post = 0
        while new_post != current_post:
            self.scoll_down_page()
            current_post = new_post
            new_post = self.get_post_count() 
            print('current_post', current_post)
            print('new_post', new_post)
            self.extract_data()
        #     if new_post > 100:
        #         break

    def extract_data(self) -> None:
        soupe = BeautifulSoup(self.page.content(), 'lxml')
        page_name = soupe.find('div', {'class':"x1e56ztr x1xmf6yo"}).text \
            if soupe.find('div', {'class':"x1e56ztr x1xmf6yo"}) else ''
        page_likes = soupe.find_all('a', {'class':"x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1s688f"})[0].text.split(' ')[0].replace('K', '000').replace('M', '000000') \
            if soupe.find_all('a', {'class':"x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1s688f"}) else 0
        page_likes = page_likes.lower().replace('k', '000').replace('m', '000000')
        page_followers = soupe.find_all('a', {'class':"x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1s688f"})[1].text.split(' ')[0].replace('K', '000').replace('M', '000000') \
            if soupe.find_all('a', {'class':"x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1s688f"}) else 0
        page_followers = page_followers.lower().replace('k', '000').replace('m', '000000')
        posts = []
        post_container = soupe.find('div', {'class':"x9f619 x1n2onr6 x1ja2u2z xeuugli xs83m0k x1xmf6yo x1emribx x1e56ztr x1i64zmx xjl7jj x19h7ccj xu9j1y6 x7ep2pv"})
        post_data = post_container.find_all('div', {'x1n2onr6 x1ja2u2z'})
        for post in post_data:
            likes = post.find('span', {'class':"xt0b8zv x2bj2ny xrbpyxo xl423tq"}).text.strip() \
                if post.find('span', {'class':"xt0b8zv x2bj2ny xrbpyxo xl423tq"}) else '0'
            likes = likes.lower().replace('k', '000').replace('m', '000000')
            description = post.find('div', {'class':"xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs x126k92a"}).text.strip() \
                if post.find('div', {'class':"xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs x126k92a"}) else ''
            cs = post.find('div', {'class':"x9f619 x1n2onr6 x1ja2u2z x78zum5 x2lah0s x1qughib x1qjc9v5 xozqiw3 x1q0g3np xykv574 xbmpl8g x4cne27 xifccgj"})
            comments = 0
            shares = 0
            if cs and cs.text:
                c = cs.find_all('span', {'dir':'auto'})
                match(len(c)):
                    case 2:
                        shares = c[1].text.lower().replace('shares', '').replace('share', '').strip().replace('k', '000').replace('m', '000000')
                        shares = int(''.join(filter(str.isdigit, shares)))
                        comments = c[0].text.lower().replace('comment', '').replace('comments', '').strip().replace('k', '000').replace('m', '000000')
                        comments = int(''.join(filter(str.isdigit, comments)))
                    case 1:
                        if 'share' in c[0].text or 'shares' in c[0].text:
                            shares = c[0].text.lower().replace('shares', '').replace('share', '').strip().replace('k', '000').replace('m', '000000')
                            shares = int(''.join(filter(str.isdigit, shares)))
                        if 'comment' in c[0].text or 'comments' in c[0].text:
                            comments = c[0].text.lower().replace('comment', '').replace('comments', '').strip().replace('k', '000').replace('m', '000000')
                            comments = int(''.join(filter(str.isdigit, comments)))

            posts.append({
                'reaction': int(''.join(filter(str.isdigit, likes))),
                'description': description,
                'comments': comments,
                'shares': shares,
                'date': ''
            })

        data = {
            'name': page_name,
            'likes': int(''.join(filter(str.isdigit, page_likes))),
            'followers': int(''.join(filter(str.isdigit, page_followers))),
            'source': 'facebook',
            'establishment': "/api/establishment/",
            'posts': posts
        }
        self.data_container.append(data)
        
                
    def save(self, data:dict) -> None:
        print('==> saving data ...')
        dict_data = json.dumps(data, indent=4)
        with open('demo.json', 'a') as openfile:
            openfile.write(dict_data)
        data.clear()

    def switch_acount(self) -> None:
        pass

if __name__=='__main__':
    print("==> program is lauching ('_')")
    t = FacebookProfileScraper()
    t.goto_login()
    t.fill_loginform()
    t.load_hotel_pages()
    for url in t.hotel_page_urls:
        print(url)
        t.goto_fb_page(url)
        t.load_page_content()
        t.extract_data()
        t.save(t.data_container)
    print("==> program finished ('_'))")
    
