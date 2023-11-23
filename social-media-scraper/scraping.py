import json
from os import path, environ
import dotenv
from datetime import datetime

dotenv.load_dotenv()


class Scraping(object):
    def __init__(self, items: list) -> None:
        self.posts = []
        self.page_data = {}
        self.items = items
        self.establishment = ''
        self.url = ''
        self.current_credential = {}

    def set_current_credential(self, index):
        self.current_credential = self.credentials[index]

    def set_credentials(self, source: str) -> None:
        logins_path = path.join(path.dirname(__file__), 'logins.json')
        with open(logins_path, 'r') as f:
            data = json.load(f)
            self.credentials = data[source]

        if len(self.credentials):
            self.set_current_credential(0)

    def set_item(self, item):
        self.establishment = item['establishment_id']
        self.url = item['url']

    def save(self):

        page_data = self.page_data
        page_data['posts'] = self.posts
        page_data['url'] = self.url
        page_data['createdAt'] = datetime.now().strftime('%Y-%m-%d')

        with open(f"{environ.get('SOCIAL_FOLDER')}/{page_data.pop('name')}_{datetime.now().strftime('%Y-%m-%d')}.json", 'w') as foutput:
            json.dump(page_data, foutput, indent=4, sort_keys=True)

        self.posts = []
        self.page_data = {}

    def stop(self):
        pass
