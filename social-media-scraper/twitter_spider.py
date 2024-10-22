import re
from playwright.sync_api import sync_playwright
from nested_lookup import nested_lookup
from random import randint
import time
from datetime import datetime, timedelta
from scraping import Scraping
from progress.bar import ChargingBar, FillingCirclesBar
from bs4 import BeautifulSoup


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


class BaseTwitterScrap(Scraping):

    def __init__(self, items: list) -> None:
        super().__init__(items)
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False, 
            args=['--start-maximized'])
        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()
        self.page.set_default_timeout(60000)

    def resolve_loginform(self) -> None:
        self.fill_loginform()
        # self.normal_login_step = 0
        while "/home" not in self.page.url:
            self.fill_loginform()
        self.page.wait_for_timeout(60000)

    def login_with_google_account(self) -> None:
        pass

    def login_with_apple_account(self) -> None:
        pass


    def goto_login(self) -> None:
        try:
            self.page.goto("https://x.com/i/flow/login", timeout=120000, wait_until='load')
            time.sleep(5)
            self.page.wait_for_timeout(60000)
        except TimeoutError:
            self.goto_login()

    def fill_loginform(self) -> None:
        time.sleep(5)
        modal_header = self.page.locator("//h1[@id='modal-header']").text_content().lower()
        print(modal_header)
        match modal_header:
        
            case 'sign in to x':
                self.page.wait_for_selector(
                    "//input[@autocomplete='username']")
                self.page.locator("//input[@autocomplete='username']").click()
                time.sleep(randint(1, 3))
                print(self.current_credential)
                self.page.locator("//input[@autocomplete='username']").fill(self.current_credential['email'])
                self.page.locator(
                    "//span[text()='Next' or text()='Next']").click()
                self.page.wait_for_timeout(10000)
                time.sleep(randint(1, 3))

            case 'connectez‑vous à x':
                self.page.wait_for_selector("//input[@autocomplete='username']", timeout=10000)
                self.page.locator("//input[@autocomplete='username']").click()
                time.sleep(randint(1, 3))
                self.page.locator("//input[@autocomplete='username']").fill(self.current_credential['email'])
                self.page.locator(
                    "//span[text()='Next' or text()='Suivant']").click()
                self.page.wait_for_timeout(10000)
                time.sleep(randint(1, 3))

            case "enter your phone number or username":
                self.page.locator(
                    "//input[@data-testid='ocfEnterTextTextInput']").click()
                time.sleep(randint(1, 3))
                self.page.locator("//input[@data-testid='ocfEnterTextTextInput']").fill(self.current_credential['username'])
                self.page.locator(
                    "//span[text()='Next' or text()='Next']").click()
                self.page.wait_for_timeout(10000)
                time.sleep(randint(1, 3))

            case "entrez votre adresse email ou votre nom d'utilisateur.":
                self.page.locator(
                    "//input[@data-testid='ocfEnterTextTextInput']").click()
                time.sleep(randint(1, 3))
                self.page.locator("//input[@data-testid='ocfEnterTextTextInput']").fill(self.current_credential['username'])
                self.page.locator("//button[@data-testid='ocfEnterTextNextButton']").click()
                self.page.wait_for_timeout(10000)
                time.sleep(randint(1, 3))

            case "enter your password":
                self.page.locator("//input[@type='password']").click()
                time.sleep(randint(1, 3))
                self.page.locator("//input[@type='password']").fill(self.current_credential['password'])
                self.page.locator("//span[text()='Log in']").click()
                self.page.wait_for_timeout(10000)
                time.sleep(randint(1, 3))

            case "entrez votre mot de passe":
                self.page.locator("//input[@type='password']").click()
                time.sleep(randint(1, 3))
                self.page.locator("//input[@type='password']").fill(self.current_credential['password'])
                self.page.locator("//span[text()='Log in' or text()='Se connecter']").click()
                self.page.wait_for_timeout(10000)
                time.sleep(randint(1, 3))
                self.normal_login_step += 1

            case 'check your email':
                print('code checking')
                self.page.locator("//input[@data-testid='ocfEnterTextTextInput']").click()
                code = input('code de confirmation: ')
                self.page.locator("//input[@data-testid='ocfEnterTextTextInput']").fill(code)
                self.page.wait_for_timeout(10000)
                self.page.locator("//span[text()='Next' or text()='Suivant']").click()
                time.sleep(randint(1, 3))


            case _:
                print('none')
                self.goto_login()

    def log_out(self) -> None:
        self.page.locator(
            "//span[text()='{}']".format(self.current_credential['username'])).click()
        time.sleep(.5)
        self.page.locator(
            "//span[text()='Log out {}']".format(self.current_credential['username'])).click()
        time.sleep(.5)
        self.page.locator("//span[text()='Log out']").click()


    def format_date(self, time_str:str) -> str:
        input_format = "%a %b %d %H:%M:%S %z %Y"
        output_format = "%d/%m/%Y"
        formatted_time = datetime.strptime(time_str, input_format).strftime(output_format)
        return formatted_time

    def format_text(self, text:str) -> str:
        if text != '':
            text = text.split(' ')
            text = [x for x in text if not x.startswith('@')]
            text = ' '.join(text)
        return text

    def execute(self):
        # progress = ChargingBar('Preparing ', max=3)
        self.goto_login()
        self.set_credentials('twitter')
        # progress.next()
        print("==> filling login page")
        self.resolve_loginform()


class TwitterScraper(BaseTwitterScrap):

    def __init__(self, items: list) -> None:
        super().__init__(items)
        self.xhr_calls = {
            'profile': {},
            'tweets': [],
            'tweets_detail':[]
        }
        self.last_date = ""
        self.detail_urls = []

    def scroll_down_page(self) -> None:
        print('scrolling down')
        preview_date = ''
        last_date = self.get_post_last_date()
        while last_date > (datetime.now() - timedelta(days=365)):
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(3)
            preview_date = last_date
            last_date = self.get_post_last_date()
            if type(last_date) == str or last_date == preview_date:
                response = input('Do you want to continue  reload yes or no?:')
                if response.lower() == 'yes':
                    last_date = preview_date
                else:
                    break
        time.sleep(3)


    def scroll_page(self, max_scrolls:int=50) -> None:
        prev_height = -1
        scroll_count = 0
        while scroll_count < max_scrolls:
            self.page.on("response", self.intercept_page_response)
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            new_height = self.page.evaluate("document.body.scrollHeight")
            if new_height == prev_height:
                break
            prev_height = new_height
            scroll_count += 1
            time.sleep(3)
        time.sleep(3)

    def intercept_page_response(self,response) -> None:
        """capture all background requests and save them"""
        response_type = response.request.resource_type
        if response_type == "xhr":
            if 'UserBy' in response.url:
                self.xhr_calls['profile'] = response.json()
            if 'UserTweets' in response.url:
                self.xhr_calls['tweets'].append(response.json())

    def intercept_detail_page_response(self,response) -> None:
        """capture all background requests and save them"""
        response_type = response.request.resource_type
        if response_type == "xhr":
            if 'TweetDetail' in response.url:
                self.xhr_calls['tweets_detail'].append(response.json())

    def goto_tweet_page(self) -> None:
        self.page.on("response", self.intercept_page_response)
        self.page.goto(self.url)
        self.page.wait_for_timeout(10000)
        time.sleep(4)

    def goto_detail_pages(self, url:str) -> None:
        print(url)
        self.page.on('response', self.intercept_detail_page_response)
        self.page.goto(url)
        self.page.wait_for_timeout(10000)
        self.scroll_page(10)
        time.sleep(5)

    def extract_tweet_detail_link(self) -> None:
        link_data = nested_lookup(key='expanded_url', document=self.xhr_calls['tweets'])
        links = list(set(link_data))
        for link in links:
            if f"{self.page.url}/status/" in link:
                self.detail_urls.append(link.replace('/photo/1', '').replace('/video/1', ''))
        self.detail_urls = list(set(self.detail_urls))
        print(self.detail_urls)

    def navigate_detail_page(self) -> None:
        print(f"{len(self.detail_urls)} url detail found")
        for i in range(len(self.detail_urls)):
            print(f"{i + 1} / {len(self.detail_urls)}")
            self.goto_detail_pages(self.detail_urls[i])
            self.extract_posts()
            self.xhr_calls['tweets_detail'].clear()

    def get_post_last_date(self) -> object:
        try:
            date_container = nested_lookup(key='content', document=self.xhr_calls['tweets'][-1])
            if date_container:
                print(len(date_container))
                for i in range(len(date_container)):
                    print(i)
                    data = date_container[i]
                    if i == 0:
                        if data['entryType'] == 'TimelineTimelineItem':
                            date = data['itemContent']['tweet_results']['result']['legacy']['created_at']
                            new_last_date = self.format_date(date)
                            self.last_date = datetime.strptime(new_last_date, "%d/%m/%Y")
                            print(f'last date first {self.last_date}')
                    else:
                        if data['entryType'] == 'TimelineTimelineItem':
                            date = data['itemContent']['tweet_results']['result']['legacy']['created_at']
                            new_date_other = self.format_date(date)
                            new_date = datetime.strptime(new_date_other, "%d/%m/%Y")
                            if new_date < self.last_date:
                                self.last_date = new_date
                            print(f'last date time {self.last_date}')
                        # elif data['entryType'] == 'TimelineTimelineModule':
                        #     print(data['entryType'])
                        #     date = data['items'][0]['item']['itemContent']['user_results']['result']['legacy']['created_at']
                        #     new_date_other = self.format_date(date)
                        #     new_date = datetime.strptime(new_date_other, "%d/%m/%Y")
                        #     if new_date < last_date:
                        #         last_date = new_date
                        #     print(f'last date {last_date}')
                return self.last_date
            else:
                print('No data container found')
                return self.last_date
        except KeyError:
            print('error geting date')
            return self.last_date

    
    def extract_posts(self) -> None:
        print('extract post')
        tweet_data_container = nested_lookup(key='entries', document=self.xhr_calls['tweets_detail'])
        for tweet in tweet_data_container:
            post = {'comment_values':[]}
            for item in tweet:
                if item['content']['entryType'] == 'TimelineTimelineItem':
                    comment_section = item['content']['itemContent']['tweet_results']['result']['legacy']
                    post['post_url'] = self.page.url
                    post['author'] = self.name
                    post['description'] =  self.remove_non_utf8_characters(self.format_text(comment_section['full_text']))
                    post['reaction'] = comment_section['favorite_count']
                    post['shares'] = comment_section['retweet_count']
                    post['publishedAt'] = self.format_date(comment_section['created_at']) 
                    post['comments'] = comment_section['reply_count']
                    post['hashtag'] = ''
                    post['comment_values'] = []
                
                if item['content']['entryType'] == 'TimelineTimelineModule':
                    try:
                        comment_section = item['content']['items'][0]['item']['itemContent']['tweet_results']['result']
                        print('passed')
                        post['comment_values'].append({
                            'author': comment_section['core']['user_results']['result']['legacy']['name'],
                            'author_page_url': "https://x.com/" + comment_section['core']['user_results']['result']['legacy']['screen_name'],
                            'comment': self.remove_non_utf8_characters(self.format_text(comment_section['legacy']['full_text'])),
                            'likes': comment_section['legacy']['favorite_count'],
                            'published_at': self.format_date(comment_section['legacy']['created_at'])
                        })
                    except Exception as e:
                        print(post['comments'])
                        print(e)
                        print('No comment')
                        pass
            if datetime.strptime(post['publishedAt'], "%d/%m/%Y") > (datetime.now() - timedelta(days=365)):
                if post['comments'] != len(post['comment_values']):
                    post['comments'] = len(post['comment_values'])
                print(post)
                self.posts.append(post)

            self.xhr_calls['tweets_detail'].clear()
            

    def extract_profile(self) -> None:
        profile_data_container = nested_lookup(key='legacy', document=self.xhr_calls['profile'])[0]
        self.page_data['followers'] = profile_data_container['followers_count']
        self.page_data['establishement'] = self.establishment
        self.page_data['likes'] = profile_data_container['followers_count']
        self.page_data['createdAt'] = self.format_date(profile_data_container['created_at'])
        self.page_data['hasStat'] = "1"
        self.page_data['source'] = "twitter"
        self.page_data['name'] = f"twitter_{profile_data_container['name']}"
        self.name = profile_data_container['name']
        print(self.page_data)
        

    def execute(self):
        super().execute()
        output_files = []
        for item in self.items:
            # try:
            # p_item = FillingCirclesBar(item['establishment_name'], max=4)
            self.set_item(item)
            # p_item.next()
            print(" | Open page")
            self.goto_tweet_page()
            self.scroll_down_page()
            # p_item.next()
            print(" | Extracting")
            self.extract_profile()
            self.extract_tweet_detail_link()
            time.sleep(4)
            self.navigate_detail_page()
            # p_item.next()
            print('posts extractions')
            self.extract_posts()
            print(" | Saving")
            print(self.page_data)
            output_files.append(self.save())
            # p_item.next()
            print(" | Saved")
            # except:
            #     pass

        self.stop()
        return output_files


class TwitterProfileScraper(Scraping):

    def __init__(self, items: list = []) -> None:
        super().__init__(items)

        self.hotel_page_urls = []
        self.xhr_calls = {}
        self.data_container = {}

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
                        headless=False, 
            args=['--start-maximized']
        )
        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()
        self.page.set_default_timeout(60000)


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
        while "/home" not in self.page.url :
            self.fill_loginform()
        print(' ==> login done')
        self.page.wait_for_timeout(60000)

    def goto_login(self) -> None:
        self.page.goto("https://twitter.com/i/flow/login")

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
                time.sleep(randint(5))

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
        # progress = ChargingBar('Preparing ', max=3)
        self.goto_login()
        # progress.next()
        print(" | Fill login page")
        self.resolve_loginform()
        # progress.next()
        print(" | Logged in!")
        output_files = []

        for item in self.items:
            try:
                # p_item = FillingCirclesBar(item['establishment_name'], max=4)
                self.set_item(item)
                # p_item.next()
                print(" | Open page")
                self.goto_tweet_page()
                # p_item.next()
                print(" | Extracting")
                self.extract_data()
                # p_item.next()
                print(" | Saving")
                self.save()
                # p_item.next()
                output_files.append(self.save())
                print(" | Saved")
            except:
                pass

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

            case "sing in to x":
                self.page.wait_for_selector(
                    "//input[@autocomplete='username']")
                self.page.locator("//input[@autocomplete='username']").click()
                time.sleep(randint(1, 3))
                self.page.fill(
                    "//input[@autocomplete='username']", self.current_credential['email'])
                self.page.locator("//span[text()='Next']").click()
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

            case 'enter your phone number or username':
                self.page.locator(
                    "//input[@data-testid='ocfEnterTextTextInput']").click()
                time.sleep(randint(1, 3))
                self.page.fill(
                    "//input[@data-testid='ocfEnterTextTextInput']", self.current_credential['username'])
                self.page.locator("//button[@data-testid='ocfEnterTextNextButton']").click()
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

            case "enter your password":
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


class X_scraper(BaseTwitterScrap):

    def __init__(self, items: list) -> None:
        super().__init__(items)
        self.post_data = []
        self.xhr_calls = {}
        self.last_date = datetime.now()

    def print_in_file(self, obj) -> None:
        with open('dates.json', 'a') as openfile:
            openfile.write(f'"{obj}", \n')

    def goto_x_page(self):
        print(f" ==> { self.url }")
        self.print_in_file(self.url)
        self.page.on("response", self.intercept_response)
        self.page.goto(self.url)
        self.page.wait_for_selector("//article[@role='article']", timeout=20000)
        #  self.page.wait_for_timeout(20000)
        #le probleme ici c'est que si la page n'existe pas il y aura une erreur donc j'essaie avec saulement le timeout pas l'attente du selecteur car elle n'existera pas si pas de page
        self.page.wait_for_timeout(10000)

    def intercept_response(self, response) -> None:
        """capture all background requests and save them"""
        response_type = response.request.resource_type
        if response_type == "xhr":
            if 'UserBy' in response.url:
                self.xhr_calls['profile'] = response.json()
            if 'UserTweets' in response.url:
                self.xhr_calls['tweets'] = response.json()

    def extract_page_data(self) -> None:
        # name = re.sub(r'[^\w]', ' ', nested_lookup(key='name', document=self.xhr_calls['profile'])[0]).strip()
        self.page_data = {
            # 'followers': nested_lookup(key='followers_count', document=self.xhr_calls['profile'])[0],
            # 'likes': nested_lookup(key='favourites_count', document=self.xhr_calls['profile'])[0],
            'source': "twitter",
            'establishment': self.establishment,
            'posts': []
            # 'name': f"twitter_{name.replace(' ', '_')}",
        }
        print(self.page_data)

    def goto_post(self, url:str) -> None:
        print(f" ==> { url }")
        try:
            self.page.goto(url)
            self.page.wait_for_selector("//article[@role='article']", timeout=10000)
            self.page.wait_for_timeout(10000)
        except TimeoutError:
            self.page.goto(url)
            self.page.wait_for_selector("//article[@role='article']", timeout=10000)
            self.page.wait_for_timeout(10000)
            

    def format_date(self, time_str: str) -> datetime | None:
        with open('dates.json', 'a') as openfile:
            openfile.write(f'"{time_str}",\n')
        if ',' in time_str and len(time_str.split(' ')) == 3:
            date = datetime.strptime(time_str, "%b %d, %Y")
            return date
        if len(time_str.split(' ')) == 2:
            time_str += f' {datetime.now().year}'
            date = datetime.strptime(time_str, "%b %d %Y")
            return date
        if 'hours ago' in time_str or 'minutes ago':
            return datetime.now()
        
    
    def format_date_from_iso(self, time_str:str) -> str:
        datetime_obj = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        return datetime_obj.strftime("%Y-%m-%d")

    def get_articles(self) -> object | None:
        articles = self.page.query_selector_all("//article[@role='article']")
        print(f"{len(articles)} articles found")
        if articles:
            return articles
        return 
    
    def get_last_date(self) -> object | None:
        articles = self.get_articles()
        article = articles[-1]
        date_link = self.extract_article(article)
        print(date_link)
        return self.format_date(date_link['date'])
    
    def extract_article(self, element:object) -> dict | None:
        soupe = BeautifulSoup(element.inner_html(), 'lxml')
        date_link = soupe.find('a', {'class':'css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-xoduu5 r-1q142lx r-1w6e6rj r-9aw3ui r-3s2u2q r-1loqt21'}, href=True)
        date = date_link['aria-label']
        link = date_link['href']
        if date and link:
            return {'date':date, 'link': f'https://x.com{link}'}
        else:
            print('date and link not found')
            return
        
    def load_more_articles(self) -> None:
        print('scroolling')
        for _ in range(3): 
            self.page.evaluate('window.scrollBy(0, window.innerHeight);')
            time.sleep(3)

    def load_and_extract(self) -> None:
        # article.evaluate('(element) => element.scrollIntoView({ behavior: "smooth", block: "center", inline: "center" })')
        articles = self.get_articles()
        if articles:
            while True:
                self.extract_post_link()
                last_date = self.get_last_date()
                if last_date <= (datetime.now() - timedelta(days=40)):
                    break
                else:
                    self.load_more_articles()
        else:
            print('No articles found')

    def extract_post_link(self) -> None:
        articles = self.get_articles()
        for article in articles:
            data = self.extract_article(article)
            self.print_in_file(data)
            if self.format_date(data['date']) <= (datetime.now() - timedelta(days=40)):
                break
            else:
                self.post_data.append(data)

    def load_comments(self) -> None:
        current_articles = len(self.get_articles())
        new_articles_count = current_articles
        while True:
            self.load_more_articles()
            new_articles_count = len(self.get_articles())
            if new_articles_count == current_articles:
                break

    def parse_int(self, text:str) -> int:
        likes = text.lower().replace('.', '').replace(',', '').replace('\xa0', '')
        if 'k' in likes:
            likes = int(float(likes.replace('k', '')) * 1000)
        if 'm' in likes:
            likes = int(float(likes.replace('m', '')) * 1000000)
        return likes

    def extract_posts(self):
        soupe = BeautifulSoup(self.page.content(), 'lxml')
        post = {'comment_values':[]}
        articles = soupe.find_all('article', {'data-testid':'tweet'})
        art = articles[0]
        post['post_url'] = self.page.url
        post['author'] = art.find('a', {'class':'css-175oi2r r-1wbh5a2 r-dnmrzs r-1ny4l3l r-1loqt21', 'role':'link'}).text
        try:
            post['description'] = self.format_text(art.find('div', {'data-testid':'tweetText'}).text)
        except:
            post['description'] = ''
        post['publishedAt'] = self.format_date_from_iso(art.find('time')['datetime'])
        try:
            post['reaction'] = int(self.parse_int(art.find('button', {'data-testid':'like'}).text.lower()))
        except:
            post['reaction'] = 0
        try:
            post['shares'] = int(soupe.find('button', {'data-testid':'retweet'}).text)
        except:
            post['shares'] = 0
        post['hashtag'] = ""
        
        articles = articles[1:]
        print(f"{len(articles)} comments found")
        for article in articles:
            comment = {}
            comment['author'] = article.find('a', {'class':'css-175oi2r r-1wbh5a2 r-dnmrzs r-1ny4l3l r-1loqt21', 'role':'link'}).text
            try:
                comment['comment'] = self.format_text(article.find('div', {'data-testid':'tweetText'}).text)
            except:
                comment['comment'] = ""
            comment['author_page_url'] = "https://x.com" + article.find('a', {'class':'css-175oi2r r-1wbh5a2 r-dnmrzs r-1ny4l3l r-1loqt21', 'role':'link'}, href=True)['href']
            try:
                comment['likes'] = int(article.find('button', {'data-testid':'like'}).text)
            except:
                comment['likes'] = 0
            comment['publishedAt'] = self.format_date_from_iso(article.find('time')['datetime'])
            post['comment_values'].append(comment)

        post['comments'] = len(post['comment_values'])
        self.page_data['posts'].append(post)

        print('extraction done')


    def post_data(self):
        pass

    def execute(self):
        super().execute()
        output_files = []

        for item in self.items:
            print(item)
            self.set_item(item)
            self.goto_x_page()
            # self.extract_page_data() j'ai commenté ça car il me semble qu'on a juste besoin des comments pour le social media puisque les score sont scrapé dans l'autre programme
            self.load_and_extract()

            if self.post_data:
                for data in self.post_data:
                    self.goto_post(data['link'])
                    self.load_comments()
                    try:
                        self.extract_posts()
                        self.save()
                        self.page_data['posts'].clear()
                    except:
                        pass
            # output_files.append(self.save())
        
        return output_files




if __name__ == '__main__':

    data = [
        # {'id': 238, 'caption': '', 'section': 'FOLLOW US', 'establishment_name': 'LUX Grand Gaube', 'establishment_id': 70, 'idprovider': 13, 'category': 'Social', 'source': 'Twitter (X)', 'url': 'https://x.com/LUXGrandGaube', 'language': 'en', 'last_review_date': None, 'last_comment_date': '01/09/2024', 'last_post_date': '03/09/2024'}, 
        # {'id': 223, 'caption': '', 'section': 'FOLLOW US', 'establishment_name': 'SOC Rugby', 'establishment_id': 69, 'idprovider': 13, 'category': 'Social', 'source': 'Twitter (X)', 'url': 'https://x.com/soc_rugby', 'language': 'fr', 'last_review_date': None, 'last_comment_date': '13/09/2024', 'last_post_date': '13/09/2024'}, 
        # {'id': 204, 'caption': '', 'section': 'FOLLOW US', 'establishment_name': 'AMSB', 'establishment_id': 63, 'idprovider': 13, 'category': 'Social', 'source': 'Twitter (X)', 'url': 'https://x.com/amsbofficiel', 'language': 'fr', 'last_review_date': None, 'last_comment_date': '03/09/2024', 'last_post_date': '05/09/2024'}, 
        # {'id': 177, 'caption': None, 'section': 'FOLLOW US', 'establishment_name': 'Sport2000 France', 'establishment_id': 52, 'idprovider': 13, 'category': 'Social', 'source': 'Twitter (X)', 'url': 'https://x.com/https://x.com/SPORT2000France', 'language': 'fr', 'last_review_date': None, 'last_comment_date': '25/06/2024', 'last_post_date': '30/08/2024'}, 
        {'id': 161, 'caption': None, 'section': 'FOLLOW US', 'establishment_name': 'Team Chambé', 'establishment_id': 49, 'idprovider': 13, 'category': 'Social', 'source': 'Twitter (X)', 'url': 'https://x.com/TeamChambe', 'language': 'fr', 'last_review_date': None, 'last_comment_date': '02/09/2024', 'last_post_date': '03/09/2024'}, 
        # {'id': 127, 'caption': None, 'section': None, 'establishment_name': 'Hotel Chamartín The One', 'establishment_id': 28, 'idprovider': 13, 'category': 'Social', 'source': 'Twitter (X)', 'url': 'https://x.com/ChamartinTheOne', 'language': 'es', 'last_review_date': None, 'last_comment_date': '08/03/2024', 'last_post_date': '07/03/2024'}, 
        # {'id': 99, 'caption': None, 'section': None, 'establishment_name': 'Le Château de Candie', 'establishment_id': 4, 'idprovider': 13, 'category': 'Social', 'source': 'Twitter (X)', 'url': 'https://x.com/chateaudecandie', 'language': 'fr', 'last_review_date': None, 'last_comment_date': '31/08/2024', 'last_post_date': '31/08/2024'}, 
        # {'id': 91, 'caption': None, 'section': None, 'establishment_name': 'Hotel Chamartín The One', 'establishment_id': 28, 'idprovider': 13, 'category': 'Social', 'source': 'Twitter (X)', 'url': 'https://x.com/ChamartinTheOne', 'language': 'es', 'last_review_date': None, 'last_comment_date': '08/03/2024', 'last_post_date': '07/03/2024'}, 
        # {'id': 66, 'caption': None, 'section': None, 'establishment_name': 'ESF Chamonix', 'establishment_id': 23, 'idprovider': 13, 'category': 'Social', 'source': 'Twitter (X)', 'url': 'https://x.com/chamonixesf', 'language': 'fr', 'last_review_date': None, 'last_comment_date': None, 'last_post_date': None}, 
        # {'id': 22, 'caption': None, 'section': None, 'establishment_name': 'Madame Vacances', 'establishment_id': 7, 'idprovider': 13, 'category': 'Social', 'source': 'Twitter (X)', 'url': 'https://x.com/Madame_Vacances', 'language': 'fr', 'last_review_date': None, 'last_comment_date': '01/07/2024', 'last_post_date': '29/08/2024'}
        ]


    t = X_scraper(
        items=data
    )
    t.execute()