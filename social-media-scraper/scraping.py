import json
from os import path


class Scraping(object):
    def __init__(self, items: list) -> None:
        # self.credentials = {
        #     'email': 'sonalimampiemo@gmail.com',
        #     'password': 'Kl#23pol106',
        #     'phone_number': '0340851090',
        #     'username': '@sonalimampiemo'
        # }
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
        print(self.page_data)

        if len(self.posts):
            print(self.posts[0])

        self.posts = []
        self.page_data = {}

    def stop(self):
        pass
