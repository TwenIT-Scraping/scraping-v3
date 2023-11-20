from twitter_spider import TwitterProfileScraper, TwitterProfileScraperFR
from models import Settings
from facebook_scraper import FacebookProfileScraper
from instagram_scraper import InstagramProfileScraper
from tiktok_spider import TikTokProfileScraper
from linkedIn_spider import LinkedInProfileScraper
import random
# from changeip import refresh_connection
import time

__class_name__ = {
    # 'Facebook': FacebookProfileScraper,
    # 'Youtube': FacebookProfileScraper,
    'Instagram': InstagramProfileScraper,
    'Linkedin': LinkedInProfileScraper,
    'facebook EN': FacebookProfileScraper,
    'Twitter': TwitterProfileScraperFR,
    'Twitter (X)': TwitterProfileScraperFR,
    'Tiktok': TikTokProfileScraper,
    'Facebook': FacebookProfileScraper
}


class ListScraper:
    def __init__(self):
        self.settings = None

    def init(self, eid=None, ename=None, categ='Social', source=None):
        self.settings = Settings(categ, eid, source, ename)
        print("Preparing settings list")
        self.settings.prepare()
        print(self.settings.items)

    def start(self):
        # refresh_connection()

        counter = 0
        by_source = {}

        # print(self.settings.items)

        print(self.settings.items)

        for source in __class_name__.keys():
            by_source[source] = [
                item for item in self.settings.items if item['source'] == source]

        for item_key in by_source.keys():
            time.sleep(random.randint(1, 3))
            if item_key in __class_name__.keys() and len(by_source[item_key]):
                print(f"****** {item_key} ******")
                try:
                    instance = __class_name__[item_key](
                        items=by_source[item_key])
                    instance.execute()
                except Exception as e:
                    print(e)
