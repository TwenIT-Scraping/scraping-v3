from playwright.sync_api import sync_playwright
from nested_lookup import nested_lookup
from random import randint
import time
import json

class FacebookProfileScraper(object):

    def __init__(self) -> None:
        print('==> initializing twitter scraper ...')
        self.credentials = {
            'email': '',
            'password': 'dev#4015',
            'phone_number': '0345861628'
        }
        self.hotel_page_urls = []
        self.xhr_calls = []
        self.data_container = {}

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
        self.page.wait_for_selector("[id='email']", timeout=30000)
        self.page.locator("[id='email']").click()
        time.sleep(.5)
        self.page.fill("[id='email']", self.credentials['phone_number'])
        time.sleep(.3)
        self.page.locator("[id='pass']").click()
        time.sleep(.2)
        self.page.fill("[id='pass']", self.credentials['password'])
        time.sleep(.1)
        self.page.locator("[type='submit']").click()
        print('==> submitted ...')
        self.page.wait_for_timeout(70000)

    def load_hotel_pages(self) -> None:
        print('==> loading all hotels twitter pages ...')
        self.hotel_page_urls = [
            "https://www.facebook.com/TheRoxyHotelNYC"
        ]

    def intercept_response(self, response) -> None:
        """capture all background requests and save them"""
        response_type = response.request.resource_type
        self.xhr_calls.append(response.text)
    
    def goto_fb_page(self, url:str) -> None:
        self.page.on("response", self.intercept_response)
        self.page.goto(url, timeout=80000)
        time.sleep(3)

    def get_json_content(self, item:object, key:str) -> object:
        try:
            return item[key]
        except KeyError:
            return ''

    def extract_data(self) -> dict:
        print("==> extracting data ...")
        
                
    def save(self) -> None:
        print('==> saving data ...')
        print(self.xhr_calls)

    def switch_acount(self) -> None:
        pass

if __name__=='__main__':
    print("==> program is lauching ('_')")
    t = FacebookProfileScraper()
    t.goto_login()
    t.fill_loginform()
    t.load_hotel_pages()
    for url in t.hotel_page_urls:
        t.goto_fb_page(url=url)
        t.extract_data()
        t.save()
    print("==> program finished ('_'))")
    
