import re
from playwright.sync_api import sync_playwright
from nested_lookup import nested_lookup
from random import randint
import time
from datetime import datetime, timedelta
from scraping import Scraping
from progress.bar import ChargingBar, FillingCirclesBar

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


class BaseTwitterSrap(Scraping):

    def __init__(self, items: list) -> None:
        super().__init__(items)
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False, 
            args=['--start-maximized'],
            timeout=60000)
        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()

    def resolve_loginform(self) -> None:
        self.fill_loginform()
        while self.page.url != "https://twitter.com/home":
            self.fill_loginform()
        self.page.wait_for_timeout(60000)

    def goto_login(self) -> None:
        self.page.goto("https://twitter.com/i/flow/login", timeout=60000, wait_until='load')
        time.sleep(5)
        self.page.wait_for_timeout(60000)

    def fill_loginform(self) -> None:
        time.sleep(5)
        modal_header = self.page.locator("//h1[@id='modal-header']").text_content().lower()
        match modal_header:
            case 'sign in to x':
                self.page.wait_for_selector(
                    "//input[@autocomplete='username']")
                self.page.locator("//input[@autocomplete='username']").click()
                time.sleep(randint(1, 3))
                print(self.current_credential)
                self.page.locator("//input[@autocomplete='username']").fill(self.current_credential['email'])
                self.page.locator(
                    "//span[text()='Next' or text()='Suivant']").click()
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
                    "//span[text()='Next' or text()='Suivant']").click()
                self.page.wait_for_timeout(10000)
                time.sleep(randint(1, 3))

            case "entrez votre adresse email ou votre nom d'utilisateur.":
                self.page.locator(
                    "//input[@data-testid='ocfEnterTextTextInput']").click()
                time.sleep(randint(1, 3))
                self.page.locator("//input[@data-testid='ocfEnterTextTextInput']").fill(self.current_credential['username'])
                self.page.locator("//span[text()='Next' or text()='Suivant']").click()
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
            text = text.replace('\n', ' ')
        return text

    def execute(self):
        # progress = ChargingBar('Preparing ', max=3)
        self.goto_login()
        self.set_credentials('twitter')
        # progress.next()
        print("==> filling login page")
        self.resolve_loginform()


class TwitterScraper(BaseTwitterSrap):

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
                    post['author'] = self.name
                    post['description'] =  self.format_text(comment_section['full_text'])
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
                            'comment': self.format_text(comment_section['legacy']['full_text']),
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
            args=['--start-maximized'],
            timeout=60000
        )
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
        print(' ==> login done')
        self.page.wait_for_timeout(60000)

    def goto_login(self) -> None:
        self.page.goto("https://twitter.com/i/flow/login", timeout=60000, wait_until='load')
        self.page.wait_for_timeout(60000)

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
        progress = ChargingBar('Preparing ', max=3)
        self.goto_login()
        progress.next()
        print(" | Fill login page")
        self.resolve_loginform()
        progress.next()
        print(" | Logged in!")
        output_files = []

        for item in self.items:
            try:
                p_item = FillingCirclesBar(item['establishment_name'], max=4)
                self.set_item(item)
                p_item.next()
                print(" | Open page")
                self.goto_tweet_page()
                p_item.next()
                print(" | Extracting")
                self.extract_data()
                p_item.next()
                print(" | Saving")
                self.save()
                p_item.next()
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
