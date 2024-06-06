import json
from os import path, environ
import dotenv
from datetime import datetime
import re

dotenv.load_dotenv()


class Scraping(object):
    def __init__(self, items: list) -> None:
        self.posts = []
        self.page_data = {}
        self.items = items
        self.establishment = ''
        self.url = ''
        self.current_credential = {}
        self.env = 'DEV'
        self.log = ''
        self.errors = False
        self.establishment_name = ''

    def set_environ(self, env):
        self.env = env

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
        self.establishment_name = item['establishment_name']

    def add_logging(self, message):
        self.log = self.log + message + '\n'

    def add_error(self, error):
        self.errors = True
        self.log = ' '.join(
            [self.log, 'An exception occurred:', type(error).__name__, "–", str(error)]) + '\n'

    def reset_error(self):
        self.errors = False

    def get_log(self):
        return self.log

    def has_errors(self):
        return self.errors

    def save(self):

        try:
            page_data = self.page_data
            page_data['posts'] = 0
            page_data['createdAt'] = datetime.now().strftime('%Y-%m-%d')

            d = json.dumps(
                self.page_data, separators=(',', ':'))
            self.add_logging(f"Data: {d}")

            # e_name = re.sub(r'[^a-zA-Z0-9\s]+', '',
            #                 page_data.pop('name')).replace(' ', '_')

            output_file = f"{page_data['source']}_score_{self.env}_{self.establishment}_{self.establishment_name}_{datetime.now().strftime('%Y-%m-%d')}"

            with open(f"{environ.get('SOCIAL_FOLDER')}/{output_file}.json", 'w') as foutput:
                json.dump(page_data, foutput, indent=4, sort_keys=True)

            self.posts = []
            self.page_data = {}

            return output_file

        except Exception as e:
            print(e)

    def stop(self):
        pass
