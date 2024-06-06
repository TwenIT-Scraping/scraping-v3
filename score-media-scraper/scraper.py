from datetime import datetime
import json
import os
from twitter_spider import TwitterProfileScraper, TwitterProfileScraperFR, TwitterScraper
from models import Settings
from facebook_scraper import FacebookProfileScraper
from instagram_scraper import InstagramProfileScraper
from tiktok_spider import TikTokProfileScraper
from linkedIn_spider import LinkedInProfileScraper
from youtube_scraper import YoutubeProfileScraper
import random
from changeip import refresh_connection
import time
import pathlib
from api import ERApi
from progress.bar import ChargingBar

__class_name__ = {
    # 'Facebook': FacebookProfileScraper,
    'Youtube': YoutubeProfileScraper,
    'Instagram': InstagramProfileScraper,
    'Linkedin': LinkedInProfileScraper,
    'facebook EN': FacebookProfileScraper,
    'Twitter': TwitterScraper,
    'Twitter (X)': TwitterScraper,
    'Tiktok': TikTokProfileScraper,
    'Facebook': FacebookProfileScraper
}


class ListScraper:
    def __init__(self, env: str):
        self.settings = None
        self.auto_save = False
        self.env = env
        self.log = ''

    def init(self, eid=None, ename=None, categ='Social', source=None):
        self.settings = Settings(categ, eid, source, ename, env=self.env)
        self.settings.prepare()

    def set_auto_save(self):
        self.auto_save = True

    def add_logging(self, message):
        self.log = self.log + message + '\n'

    def get_logging(self):
        return self.log

    def add_error(self, error):
        self.log = ' '.join(
            [self.log, 'An exception occurred:', type(error).__name__, "–", error]) + '\n'

    def get_providers(self):
        try:
            res = ERApi(entity='provider/list?categ=Social',
                        env=self.env).execute()
        except Exception as e:
            print(e)

        return {
            "providers": list(map(lambda x: x['name'], res['providers'])),
            "establishments": res['establishments']
        }

    def start(self):
        refresh_connection()

        counter = 0
        by_source = {}

        print(self.settings.items)

        for source in __class_name__.keys():
            by_source[source] = [
                item for item in self.settings.items if item['source'] == source]

        for item_key in by_source.keys():
            time.sleep(random.randint(1, 3))
            if item_key in __class_name__.keys() and len(by_source[item_key]):
                try:
                    instance = __class_name__[item_key](
                        items=by_source[item_key])
                    files = instance.execute()

                    print("After execute...\n")

                    self.add_logging(instance.get_log())

                    if not instance.has_errors() and self.auto_save:
                        print("Transform and upload ...")
                        for f in files:
                            self.transform_data(filename=f)
                            self.upload_data(file=f)

                except Exception as e:
                    self.add_error(e)
                    pass

    def transform_all_data(self):

        files = [pathlib.Path(f).stem for f in os.listdir(os.environ.get(
            'SOCIAL_FOLDER')) if pathlib.Path(f).suffix == '.json']
        for file in files:
            self.transform_data(file)

    def transform_data(self, filename):
        try:
            with open(f"{os.environ.get('SOCIAL_FOLDER')}/{filename}.json", 'r', encoding='utf-8') as finput:
                data = json.load(finput, strict=False)
                del data['url']
                del data['name']

            with open(f"{os.environ.get('SOCIAL_FOLDER')}/uploads/{filename}.json", 'w') as foutput:
                json.dump(data, foutput, indent=4, sort_keys=True)

        except Exception as e:
            print(e)
            self.add_error(e)

    def upload_data(self, file):

        data = {}

        try:

            with open(f"{os.environ.get('SOCIAL_FOLDER')}/uploads/{file}.json", 'r') as dinput:
                data = json.load(dinput)
                print(data)

        except Exception as e:
            self.add_error(e)

        # post = ERApi(method='post', entity='social_pages', env=self.env)

        # post.set_body(data)

        # result = post.execute()

        # print(result.text)

        # self.add_logging(result.text)

    def upload_all_results(self):
        files = [pathlib.Path(f).stem for f in os.listdir(
            f"{os.environ.get('SOCIAL_FOLDER')}/uploads") if pathlib.Path(f).suffix == '.json']
        progress = ChargingBar('Processing ', max=len(files))
        for file in files:
            self.upload_data(file)
            progress.next()
            print(" | ", file)


# scraper = ListScraper()
# scraper.upload_all_results()
