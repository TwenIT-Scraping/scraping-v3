from playwright.sync_api import sync_playwright
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
import time
from scraping import Scraping
from progress.bar import ChargingBar, FillingCirclesBar


def format_linkedIn_date(date: str) -> str:
    if 'jour' in date or 'day' in date:
        date = (datetime.now(
        ) - relativedelta(hours=int(''.join(filter(str.isdigit, date))))).strftime("%d/%m/%Y")
    elif 'sem' in date or 'week' in date:
        date = (datetime.now(
        ) - relativedelta(weeks=int(''.join(filter(str.isdigit, date))))).strftime("%d/%m/%Y")
    elif 'mois' in date or 'month' in date:
        date = (datetime.now(
        ) - relativedelta(months=int(''.join(filter(str.isdigit, date))))).strftime("%d/%m/%Y")
    elif 'an' in date or 'year' in date:
        date = (datetime.now(
        ) - relativedelta(years=int(''.join(filter(str.isdigit, date))))).strftime("%d/%m/%Y")
    elif 'w' in date:
        date = (datetime.now(
        ) - relativedelta(weeks=int(''.join(filter(str.isdigit, date.split(' ')[0]))))).strftime("%d/%m/%Y")
    elif 'mo' in date:
        date = (datetime.now(
        ) - relativedelta(months=int(''.join(filter(str.isdigit, date.split(' ')[0]))))).strftime("%d/%m/%Y")
    elif 'yr' in date:
        date = (datetime.now(
        ) - relativedelta(years=int(''.join(filter(str.isdigit, date.split(' ')[0]))))).strftime("%d/%m/%Y")
    return date


class LinkedInProfileScraper(Scraping):

    def __init__(self, items: list = []) -> None:
        super().__init__(items)
        self.set_credentials('linkedin')

        self.hotel_page_urls = []
        self.xhr_calls = {}
        self.data_container = []
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False, args=['--start-maximized'])
        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()

    def stop(self):
        self.context.close()

    def scoll_down_page(self) -> None:
        for i in range(5):
            self.page.evaluate(
                "window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(20000)
            time.sleep(5)

    def goto_login(self) -> None:
        self.page.goto("https://www.linkedin.com/login/fr")
        self.page.wait_for_timeout(10000)

    def fill_loginform(self) -> None:
        self.page.wait_for_selector("[id='username']")
        self.page.locator("[id='username']").click()
        time.sleep(.5)
        self.page.fill("[id='username']", self.current_credential['email'])
        time.sleep(.8)
        self.page.locator("[id='password']").click()
        time.sleep(.8)
        self.page.fill("[id='password']", self.current_credential['password'])
        time.sleep(1)
        self.page.locator("[type='submit']").click()
        self.page.wait_for_timeout(60000)

    def goto_page(self) -> None:
        self.page.goto(self.url+'/posts/?feedView=all')
        self.page.wait_for_timeout(10000)
        self.scoll_down_page()

    def extract_data(self) -> None:
        soupe = BeautifulSoup(self.page.content(), 'lxml')
        followers = int(''.join(filter(str.isdigit, soupe.find('div', {'class': "org-top-card-summary-info-list"}).find_all(
            'div', {'class': "org-top-card-summary-info-list__info-item"})[-1].text.strip())))

        name = soupe.find(
            'section', {'class': 'org-top-card artdeco-card'}).find('h1').text.strip()

        try:
            post_container = soupe.find(
                'div', class_='scaffold-finite-scroll__content').find_all('div', class_='occludable-update')
            for post in post_container:
                try:
                    comments = int(''.join(filter(str.isdigit, post.find('li', {'class': "social-details-social-counts__item social-details-social-counts__comments social-details-social-counts__item--with-social-proof"}).text.strip().split(' ')[0]))) if \
                        post.find('li', {'class': "social-details-social-counts__item social-details-social-counts__comments social-details-social-counts__item--with-social-proof"}) else 0
                    shares = int(''.join(filter(str.isdigit, post.find('li', {'class': "social-details-social-counts__item social-details-social-counts__item--with-social-proof"}).text.strip().split(' ')[0][:-15]))) if \
                        post.find('li', {'class': "social-details-social-counts__item social-details-social-counts__item--with-social-proof"}) else 0
                    title = post.find('span', {'class': "break-words"}).text.strip(
                    ) if post.find('span', {'class': "break-words"}) else ""
                    likes = int(post.find('span', {'class': "social-details-social-counts__reactions-count"}).text.strip()) if \
                        post.find('span', {'class': "social-details-social-counts__reactions-count"}) else 0
                    self.posts.append({
                        "description": title,
                        "reaction": likes,
                        "comments": comments,
                        "shares": shares,
                        "publishedAt": format_linkedIn_date(post.find('div', {'class': "update-components-text-view break-words"}).find('span', {'class': "visually-hidden"}).text.strip())
                    })
                except:
                    pass

        except:
            pass
        self.page_data = {
            'followers': followers,
            'likes': 0,
            'source': "linkedin",
            'establishment': self.establishment,
            'name': f"linkedin_{name}",
            'posts': len(self.posts)
        }

    def execute(self) -> None:
        progress = ChargingBar('Preparing ', max=2)
        self.goto_login()
        progress.next()
        print(" | Open login page")
        self.fill_loginform()
        progress.next()
        print(" | Logged in!")
        for item in self.items:
            p_item = FillingCirclesBar(item['establishment_name'], max=4)
            try:
                self.set_item(item)
                p_item.next()
                print(" | Open page")
                self.goto_page()
                p_item.next()
                print(" | Extracting")
                self.extract_data()
                p_item.next()
                print(" | Saving")
                self.save()
                p_item.next()
                print(" | Saved !")
            except:
                pass

        self.stop()
