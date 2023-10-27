from playwright.sync_api import sync_playwright
from nested_lookup import nested_lookup
from random import randint
import time
import json



MONTHS = {
    'jan': '01',
    'feb': '02',
    'mar': '03',
    'apr': '04',
    'may': '05',
    'jun': '06',
    'jul': '07',
    'aug': '08',
    'sep': '09',
    'oct': '10',
    'nov': '11',
    'dec': '12'
}


class TwitterProfileScraper(object):

    def __init__(self) -> None:
        print('==> initializing twitter scraper ...')
        self.credentials = {
            'email': '',
            'password': '',
            'username': ''
        }
        self.hotel_page_urls = []
        self.xhr_calls = {}
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
        while self.page.url != "https://twitter.com/home":
            self.fill_loginform()
        self.page.wait_for_timeout(10000)

    def goto_login(self) -> None:
        print('==> logging In ...')
        self.page.goto("https://twitter.com/i/flow/login")
        self.page.wait_for_timeout(30000)

    def log_out(self) -> None:
        print('==> Loggin out ...')
        self.page.locator("//span[text()='{}']".format(self.credentials['username'])).click()
        time.sleep(.5)
        self.page.locator("//span[text()='Log out {}']".format(self.credentials['username'])).click()
        time.sleep(.5)
        self.page.locator("//span[text()='Log out']").click()

    def fill_loginform(self) -> None:
        print('==> filling login form ...')
        time.sleep(5)
        match self.page.locator("//h1[@id='modal-header']").text_content().lower():

            case 'sign in to x':
                self.page.wait_for_selector("//input[@autocomplete='username']")
                self.page.locator("//input[@autocomplete='username']").click()
                time.sleep(randint(1, 3))
                self.page.fill("//input[@autocomplete='username']", self.credentials['email'])
                self.page.locator("//span[text()='Next']").click()
                self.page.wait_for_timeout(10000)
                time.sleep(randint(1, 3))

            case "enter your phone number or username":
                self.page.locator("//input[@data-testid='ocfEnterTextTextInput']").click()
                time.sleep(randint(1, 3))
                self.page.fill("//input[@data-testid='ocfEnterTextTextInput']", self.credentials['username'])
                self.page.locator("//span[text()='Next']").click()
                self.page.wait_for_timeout(10000)
                time.sleep(randint(1, 3))

            case "enter your password":
                self.page.locator("//input[@type='password']").click()
                time.sleep(randint(1, 3))
                self.page.fill("//input[@type='password']", self.credentials['password'])
                self.page.locator("//span[text()='Log in']").click()
                self.page.wait_for_timeout(10000)
                time.sleep(randint(1, 3))

            case _:
                self.goto_login()

    def load_hotel_pages(self) -> None:
        print('==> loading all hotels twitter pages ...')
        self.hotel_page_urls = [
            "https://twitter.com/TimesSquareNYC",
            "https://twitter.com/DreamDWTN",
            "https://twitter.com/HyattUnionSqNYC",
            "https://twitter.com/ChelseaPinesInn",
            "https://twitter.com/ChaletMounier",
            "https://twitter.com/TheRoxyHotelNYC",
            "https://twitter.com/Dominick_Hotels",
            "https://twitter.com/ChateaudeCandie"
        ]

    def intercept_response(self, response) -> None:
        """capture all background requests and save them"""
        response_type = response.request.resource_type
        if response_type == "xhr":
            if 'UserBy' in response.url:
                self.xhr_calls['profile'] = response.json()
            if 'UserTweets' in response.url:
                self.xhr_calls['tweets'] = response.json()
    
    def goto_tweet_page(self, url:str) -> None:
        self.page.on("response", self.intercept_response)
        self.page.goto(url)
        self.page.wait_for_timeout(10000)

    def get_json_content(self, item:object, key:str) -> object:
        try:
            return item[key]
        except KeyError:
            return ''

    def extract_data(self) -> dict:
        global MONTHS
        print("==> extracting data ...")
        self.data_container = {
            'followers': nested_lookup(key='followers_count', document=self.xhr_calls['profile'])[0],
            'likes': nested_lookup(key='favourites_count', document=self.xhr_calls['profile'])[0],
            'source': "twitter",
            'establishment': "/apit/establishement/",
            'name': nested_lookup(key='name', document=self.xhr_calls['profile'])[0],
        }

        tweets = []
        entries = nested_lookup(key='entries', document=self.xhr_calls['tweets'])[0]
        new_entries = []

        for entry in entries:
            if nested_lookup(key='tweet_results', document=entry) and not nested_lookup(key='retweeted_status_result', document=entry):
                new_entries.append(entry)

        for new_entry in new_entries:
            result = self.get_json_content(nested_lookup(key='tweet_results', document=new_entry)[0], 'result')
            if result:
                date = self.get_json_content(result['legacy'], 'created_at').lower().split(' ')
                date_pub = f"{date[2]}/{MONTHS[date[1]]}/{date[-1]}"
                tweets.append({
                    'title': self.get_json_content(result['legacy'], 'full_text'),
                    'likes': self.get_json_content(result['legacy'], 'favorite_count'),
                    'comments': self.get_json_content(result['legacy'], 'reply_count'),
                    'publishedAt': date_pub,
                    'shares': self.get_json_content(result['legacy'], 'retweet_count')
                })

        self.data_container['posts'] = tweets

                
    def save(self) -> None:
        print('==> saving data ...')
        with open('test.json', 'a') as openfile:
            data = json.dumps(self.data_container, indent=4)
            openfile.write(data)
        del self.data_container

    def switch_acount(self) -> None:
        pass

if __name__=='__main__':
    print("==> program is lauching ('_')")
    t = TwitterProfileScraper()
    t.goto_login()
    t.resolve_loginform()
    t.load_hotel_pages()
    for url in t.hotel_page_urls:
        t.goto_tweet_page(url=url)
        t.extract_data()
        t.save()
    print("==> program finished ('_'))")
    
