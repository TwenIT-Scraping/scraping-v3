from playwright.sync_api import sync_playwright
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
import time
from scraping import Scraping
from progress.bar import ChargingBar, FillingCirclesBar
import re
import sys


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
    elif 'yr' in date or 'y' in date:
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
        for i in range(15):
            self.page.evaluate(
                "window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(10000)
            time.sleep(3)

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
        try:
            captcha = self.page.locator(
                'div.body__banner-wrapper').locator('h1')
            if captcha:
                input("Press enter when you have finished captcha resolution ...")
        except:
            pass

    def goto_page(self, page) -> None:
        # self.page.goto(self.url+'/posts/?feedView=all')
        self.page.goto(self.url+page)
        self.page.wait_for_timeout(10000)
        self.scoll_down_page()

    def extract_data(self) -> None:
        def convert_count(value):
            if 'k' in value:
                tmp = value.split('k')
                millier = int(tmp[0])
                centaine = int(tmp[1]) if len(tmp) > 1 and tmp[1] != "" else 0

                return (millier*1000)+(centaine*100)
            else:
                return value

        try:
            comments_link = self.page.locator(
                "button.social-details-social-counts__count-value.t-12.hoverable-link-text").filter(has_text=re.compile("comment")).all()

            for item in comments_link:
                try:
                    item.click()
                    time.sleep(5)
                except Exception as e:
                    print(e)

        except Exception as e:
            print(e)

        while True:
            try:
                more_btn = self.page.locator(
                    "button.comments-comments-list__load-more-comments-button.artdeco-button.artdeco-button--muted.artdeco-button--1.artdeco-button--tertiary.ember-view")
                more_btn.click()
            except:
                break

        soupe = BeautifulSoup(self.page.content(), 'lxml')

        followers = soupe.find('section', {'class': "org-company-info-module__container artdeco-card full-width"}).find(
            'p', {'class': "t-14 t-normal text-align-center"}).text.strip().replace('\u202f', '').split('\xa0')[0]
        try:
            followers = convert_count(followers.split(' ')[0].lower())
        except Exception as e:
            print(e)
            sys.exit(1)

        name = soupe.find(
            'section', {'class': 'org-top-card artdeco-card'}).find('h1').text.strip()

        try:
            post_container = soupe.find(
                'div', class_='scaffold-finite-scroll__content').find_all('div', class_='occludable-update') if soupe.find(
                'div', class_='scaffold-finite-scroll__content') else []

            total_comments = 0
            if post_container:
                print(f"{len(post_container)} posts found ")
                for post in post_container:
                    try:
                        comments_container = post.find(
                            'li', {'class': "social-details-social-counts__comments"})
                        comments = 0

                        if comments_container:
                            print('comment found')
                            comments = int(
                                ''.join(filter(str.isdigit, comments_container.text.strip().split(' ')[0])))
                            # print(f"with {comments} comments")

                        comment_list = post.find_all(
                            'article', {'class': 'comments-comments-list__comment-item'})

                        comment_values = []

                        for comment in comment_list:
                            author = comment.find('span', {'class': 'comments-post-meta__name-text'}).find('span', {'aria-hidden': "true"}).text.strip(
                            ) if comment.find('span', {'class': 'comments-post-meta__name-text'}) and comment.find('span', {'class': 'comments-post-meta__name-text'}).find('span', {'aria-hidden': "true"}) else ""
                            print(f"author {author}")
                            comment_text = comment.find('span', {'class': 'comments-comment-item__main-content'}).text.strip(
                            ) if comment.find('span', {'class': 'comments-comment-item__main-content'}) else ""
                            print(f"author {comment_text}")
                            published_at = format_linkedIn_date(comment.find(
                                'time', {'class': 'comments-comment-item__timestamp'}).text.strip()) if comment.find(
                                'time', {'class': 'comments-comment-item__timestamp'}) else ""
                            print(f"published at {published_at}")
                            clikes = comment.find('button', {'class': 'comments-comment-social-bar__reactions-count'}).text.strip()
                            if clikes.isdigit() and clikes is not None and clikes != '':
                                clikes = int(clikes)
                            else:
                                clikes = 0
                            comment_values.append({
                                'comment': comment_text,
                                'published_at': published_at,
                                'likes': clikes,
                                'author': author,
                                "author_page_url": ""
                            })
                            print(comment_values)
                        # comments = int(''.join(filter(str.isdigit, post.find('li', {'class': "social-details-social-counts__comments"}).text.strip().split(' ')[0]))) if \
                        #     post.find('li', {'class': "social-details-social-counts__item social-details-social-counts__comments social-details-social-counts__item--with-social-proof"}) else 0
                        try:
                            post_author = post.find('span', class_="update-components-actor__name").find('span', class_="visually-hidden").text.strip(
                            ) if post.find('span', class_="update-components-actor__name") and post.find('span', class_="update-components-actor__name").find('span', class_="visually-hidden") else ""
                            print(f"post author {post_author}")
                        except Exception as e:
                            print(e)

                        shares = int(''.join(filter(str.isdigit, post.find('li', {'class': "social-details-social-counts__item social-details-social-counts__item--with-social-proof"}).text.strip().split(' ')[0][:-15]))) if \
                            post.find('li', {'class': "social-details-social-counts__item social-details-social-counts__item--with-social-proof"}) else 0
                        print(f"shares {shares}")
                        title = post.find('span', {'class': "break-words"}).text.strip(
                        ) if post.find('span', {'class': "break-words"}) else ""
                        print(f"tittle {title}")
                        likes = int(post.find('span', {'class': "social-details-social-counts__reactions-count"}).text.strip()) if \
                            post.find('span', {'class': "social-details-social-counts__reactions-count"}) else 0
                        print(f"likes {likes}")
                        date = post.find(
                            'span', {'class': "update-components-actor__sub-description"}).text.split() if post.find(
                            'span', {'class': "update-components-actor__sub-description"}) else ""
                        date2 = ""

                        if date:
                            date2 = post.find('span', {'class': "update-components-actor__sub-description"}).find(
                                'span', {'class': "visually-hidden"}).text.strip() or ""
                            date2 = format_linkedIn_date(date2)

                        if (date2):
                            self.posts.append({
                                "post_url": "",
                                "author": post_author,
                                "description": title,
                                "reaction": likes,
                                "comments": comments,
                                "shares": shares,
                                "publishedAt": date2,
                                'comment_values': comment_values,
                                'hashtag': ""
                            })

                        total_comments += comments
                    except Exception as e:
                        print("Exception interne")
                        print(e)
                        pass
            else:
                print(f'No post found for {name}')

        except Exception as e:
            print("Exception externe")
            print(e)
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
        output_files = []
        for item in self.items:
            p_item = FillingCirclesBar(item['establishment_name'], max=6)
            try:
                self.set_item(item)
                p_item.next()
                print(" | Open page")
                self.goto_page('/posts/?feedView=all')
                p_item.next()
                print(" | Extracting all posts")
                self.extract_data()
                p_item.next()
                self.goto_page('/posts/?feedView=articles')
                p_item.next()
                print(" | Extracting all artiles")
                self.extract_data()
                p_item.next()
                self.goto_page('/posts/?feedView=images')
                print(" | Extracting all images")
                self.extract_data()
                p_item.next()
                print(" | Saving")
                output_files.append(self.save())
                p_item.next()
                print(" | Saved !")
            except:
                pass

        self.stop()

        return output_files
