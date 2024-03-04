from datetime import datetime
import json
import os
from twitter_spider import TwitterProfileScraper, TwitterProfileScraperFR
from models import Settings
from facebook_scraper import FacebookProfileScraper
from instagram_scraper import InstagramProfileScraper
from tiktok_spider import TikTokProfileScraper
from linkedIn_spider import LinkedInProfileScraper
import random
from changeip import refresh_connection
import time
import pathlib
from api import ERApi
from progress.bar import ChargingBar

__class_name__ = {
    # 'Facebook': FacebookProfileScraper,
    # 'Youtube': FacebookProfileScraper,
    'Instagram hashtag': InstagramProfileScraper,
    'Linkedin hashtag': LinkedInProfileScraper,
    'facebook EN': FacebookProfileScraper,
    'Twitter hashtag': TwitterProfileScraperFR,
    'Twitter (X) hashtag': TwitterProfileScraperFR,
    'Tiktok hashtag': TikTokProfileScraper,
    'Facebook hashtag': FacebookProfileScraper
}


class ListScraper:
    def __init__(self, env: str):
        self.settings = None
        self.auto_save = False
        self.env = env

    def init(self, eid=None, ename=None, categ='Hashtag', source=None):
        self.settings = Settings(categ, eid, source, ename)
        self.settings.prepare()

    def set_auto_save(self):
        print("set auto save to active")
        self.auto_save = True

    def get_providers(self):
        try:
            res = ERApi(entity='provider/list?categ=Hashtag',
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

                    print("After execute...")

                    if self.auto_save:
                        print("Transform and upload ...")
                        for f in files:
                            self.transform_data(filename=f)
                            # self.upload_data(file=f)

                except Exception as e:
                    print(e)

    def transform_all_data(self):

        files = [pathlib.Path(f).stem for f in os.listdir(os.environ.get(
            'SOCIAL_FOLDER')) if pathlib.Path(f).suffix == '.json']
        for file in files:
            self.transform_data(file)

    def transform_data(self, filename):
        results = ""
        try:
            with open(f"{os.environ.get('SOCIAL_FOLDER')}/{filename}.json", 'r', encoding='utf-8') as finput:
                data = json.load(finput, strict=False)

            for item in data['posts']:
                if "publishedAt" in item.keys():
                    item['uploadAt'] = item['publishedAt']
                    del item['publishedAt']
                    try:
                        item['uploadAt'] = datetime.strptime(
                            item['uploadAt'], '%d/%m/%Y').strftime('%Y-%m-%d')
                    except Exception as e:
                        try:
                            item['uploadAt'] = datetime.strptime(
                                item['uploadAt'], '%d-%m-%Y').strftime('%Y-%m-%d')
                        except:
                            pass

                if "description" in item.keys():
                    item['title'] = item['description']

                if "reaction" in item.keys():
                    item['likes'] = item['reaction']

                if "shares" in item.keys():
                    item['share'] = item['shares']

                comments = ""

                for com in item['comment_values']:
                    comments += '|cc|'.join(
                        [com['comment'], com['author'], str(com['likes']), datetime.strptime(
                            com['published_at'], '%d/%m/%Y').strftime('%Y-%m-%d')]) + "|cl|"

                line = '|&|'.join([item['author'], item['title'], item['uploadAt'],
                                   str(item['likes']), str(item['share']), str(item['comments']), item['hashtag'], comments]) + "|*|"
                if len(line.split('|&|')) == 8:
                    results += line

            with open(f"{os.environ.get('SOCIAL_FOLDER')}/uploads/{filename}.txt", 'w', encoding='utf-8') as foutput:
                foutput.write(results)

            with open(f"{os.environ.get('SOCIAL_FOLDER')}/uploads/{filename}.json", 'w') as foutput:
                json.dump(data, foutput, indent=4, sort_keys=True)

        except Exception as e:
            print(e)
            print(filename)

    def upload_data(self, file):
        data = {}
        posts = ""

        with open(f"{os.environ.get('SOCIAL_FOLDER')}/uploads/{file}.json", 'r') as dinput:
            data = json.load(dinput)
            data['posts'] = len(data['posts'])
            del data['url']

        with open(f"{os.environ.get('SOCIAL_FOLDER')}/uploads/{file}.txt", 'r', encoding='utf-8') as pinput:
            for line in pinput.readlines():
                posts += " " + line.strip()

        data['post_items'] = posts

        post = ERApi(method='postmulti')

        post.set_body(data)

        result = post.execute()

        print(result)

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
