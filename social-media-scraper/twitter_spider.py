import re
from playwright.sync_api import sync_playwright
from nested_lookup import nested_lookup
from random import randint
import time
import json
from scraping import Scraping

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


class TwitterProfileScraper(Scraping):

    def __init__(self, items: list = []) -> None:
        super().__init__(items)

        self.hotel_page_urls = []
        self.xhr_calls = {}
        self.data_container = {}

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False, args=['--start-maximized'])
        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()

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
        while self.page.url != "https://twitter.com/home":
            self.fill_loginform()
        self.page.wait_for_timeout(10000)

    def goto_login(self) -> None:
        self.page.goto("https://twitter.com/i/flow/login")
        self.page.wait_for_timeout(30000)

    def log_out(self) -> None:
        self.page.locator(
            "//span[text()='{}']".format(self.current_credential['username'])).click()
        time.sleep(.5)
        self.page.locator(
            "//span[text()='Log out {}']".format(self.current_credential['username'])).click()
        time.sleep(.5)
        self.page.locator("//span[text()='Log out']").click()

    def fill_loginform(self) -> None:
        time.sleep(5)
        match self.page.locator("//h1[@id='modal-header']").text_content().lower():

            case 'sign in to x':
                self.page.wait_for_selector(
                    "//input[@autocomplete='username']")
                self.page.locator("//input[@autocomplete='username']").click()
                time.sleep(randint(1, 3))
                self.page.fill(
                    "//input[@autocomplete='username']", self.current_credential['email'])
                self.page.locator(
                    "//span[text()='Next' or text()='Suivant']").click()
                self.page.wait_for_timeout(10000)
                time.sleep(randint(1, 3))

            case 'connectez‑vous à x':
                self.page.wait_for_selector(
                    "//input[@autocomplete='username']")
                self.page.locator("//input[@autocomplete='username']").click()
                time.sleep(randint(1, 3))
                self.page.fill(
                    "//input[@autocomplete='username']", self.current_credential['email'])
                self.page.locator("//span[text()='Next']").click()
                self.page.wait_for_timeout(10000)
                time.sleep(randint(1, 3))

            case "enter your phone number or username":
                self.page.locator(
                    "//input[@data-testid='ocfEnterTextTextInput']").click()
                time.sleep(randint(1, 3))
                self.page.fill(
                    "//input[@data-testid='ocfEnterTextTextInput']", self.current_credential['email'])
                self.page.locator("//span[text()='Next']").click()
                self.page.wait_for_timeout(10000)
                time.sleep(randint(1, 3))

            case "enter your password":
                self.page.locator("//input[@type='password']").click()
                time.sleep(randint(1, 3))
                self.page.fill("//input[@type='password']",
                               self.current_credential['password'])
                self.page.locator("//span[text()='Log in']").click()
                self.page.wait_for_timeout(10000)
                time.sleep(randint(1, 3))

            case _:
                self.goto_login()

    def intercept_response(self, response) -> None:
        """capture all background requests and save them"""
        response_type = response.request.resource_type
        if response_type == "xhr":
            if 'UserBy' in response.url:
                self.xhr_calls['profile'] = response.json()
            if 'UserTweets' in response.url:
                self.xhr_calls['tweets'] = response.json()

    def goto_tweet_page(self) -> None:
        self.page.on("response", self.intercept_response)
        self.page.goto(self.url)
        self.page.wait_for_timeout(10000)

    def get_json_content(self, item: object, key: str) -> object:
        try:
            return item[key]
        except KeyError:
            return ''

    def extract_data(self) -> dict:
        global MONTHS

        with open("dada.json", "w") as f:
            f.write(json.dumps(self.xhr_calls, indent=4))

        name = re.sub(r'[^\w]', ' ', nested_lookup(
            key='name', document=self.xhr_calls['profile'])[0])

        self.page_data = {
            'followers': nested_lookup(key='followers_count', document=self.xhr_calls['profile'])[0],
            'likes': nested_lookup(key='favourites_count', document=self.xhr_calls['profile'])[0],
            'source': "twitter",
            'establishment': self.establishment,
            'name': f"twitter_{name}",
        }

        tweets = []
        entries = nested_lookup(
            key='entries', document=self.xhr_calls['tweets'])[0]
        new_entries = []

        for entry in entries:
            if nested_lookup(key='tweet_results', document=entry) and not nested_lookup(key='retweeted_status_result', document=entry):
                new_entries.append(entry)

        for new_entry in new_entries:
            result = self.get_json_content(nested_lookup(
                key='tweet_results', document=new_entry)[0], 'result')
            if result:
                date = self.get_json_content(
                    result['legacy'], 'created_at').lower().split(' ')
                date_pub = f"{date[2]}/{MONTHS[date[1]]}/{date[-1]}"
                tweets.append({
                    'title': self.get_json_content(result['legacy'], 'full_text'),
                    'likes': self.get_json_content(result['legacy'], 'favorite_count'),
                    'comments': self.get_json_content(result['legacy'], 'reply_count'),
                    'publishedAt': date_pub,
                    'share': self.get_json_content(result['legacy'], 'retweet_count')
                })

        self.posts = tweets

    def switch_acount(self) -> None:
        pass

    def execute(self) -> None:
        self.goto_login()
        self.resolve_loginform()

        for item in self.items:
            self.set_item(item)
            self.goto_tweet_page()
            # self.load_page_content()
            self.extract_data()
            self.save()

        self.stop()


class TwitterProfileScraperFR(TwitterProfileScraper):
    def __init__(self, items: list = []) -> None:
        super().__init__(items)
        self.set_credentials('twitter')

    def log_out(self) -> None:
        self.page.locator(
            "//span[text()='{}']".format(self.current_credential['username'])).click()
        time.sleep(.5)
        self.page.locator(
            "//span[text()='Log out {}']".format(self.current_credential['username'])).click()
        time.sleep(.5)
        self.page.locator("//span[text()='Log out']").click()

    def fill_loginform(self) -> None:
        time.sleep(5)
        match self.page.locator("//h1[@id='modal-header']").text_content().lower():
            case "connectez‑vous à x":
                self.page.wait_for_selector(
                    "//input[@autocomplete='username']")
                self.page.locator("//input[@autocomplete='username']").click()
                time.sleep(randint(1, 3))
                self.page.fill(
                    "//input[@autocomplete='username']", self.current_credential['email'])
                self.page.locator("//span[text()='Suivant']").click()
                self.page.wait_for_timeout(10000)
                time.sleep(randint(1, 3))

            case "entrez votre adresse email ou votre nom d'utilisateur.":
                self.page.locator(
                    "//input[@data-testid='ocfEnterTextTextInput']").click()
                time.sleep(randint(1, 3))
                self.page.fill(
                    "//input[@data-testid='ocfEnterTextTextInput']", self.current_credential['username'])
                self.page.locator("//span[text()='Suivant']").click()
                self.page.wait_for_timeout(10000)
                time.sleep(randint(1, 3))

            case "entrez votre mot de passe":
                self.page.locator("//input[@type='password']").click()
                time.sleep(randint(1, 3))
                self.page.fill("//input[@type='password']",
                               self.current_credential['password'])
                self.page.locator("//span[text()='Se connecter']").click()
                self.page.wait_for_timeout(10000)
                time.sleep(randint(1, 3))

            case _:
                self.page.wait_for_selector(
                    "//input[@autocomplete='username']")
                self.page.locator("//input[@autocomplete='username']").click()
                time.sleep(randint(1, 3))
                self.page.fill(
                    "//input[@autocomplete='username']", self.current_credential['email'])
                self.page.locator("//span[text()='Suivant']").click()
                self.page.wait_for_timeout(10000)
                time.sleep(randint(1, 3))
