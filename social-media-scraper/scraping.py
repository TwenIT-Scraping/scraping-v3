import json
from os import path, environ
import dotenv
from datetime import datetime
import re
import unicodedata
from api import ERApi

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
        if 'https://x.com/https://x.com' in item['url']:
            item['url'] = item['url'].replace('https://x.com/https://x.com', 'https://x.com')
        self.url = item['url']
        self.etab_name = item['establishment_name']


    def remove_non_utf8_characters(self, text:str):
        # Create an empty list to store valid characters
        text = text.replace("\n", "")
        encoded_string = r"{}".format(text)
        decoded_string = bytes(encoded_string, 'utf-8').decode('unicode-escape')
        valid_chars = []
        # Iterate through each character in the input string
        for char in decoded_string:
            try:
                # Check if the character can be normalized to NFKC form
                normalized_char = unicodedata.normalize('NFKC', char)
                # Encode the normalized character to utf-8 to check if it's valid
                normalized_char.encode('utf-8')
                # If successful, add it to the list of valid characters
                valid_chars.append(char)
            except UnicodeEncodeError:
                # If encoding to utf-8 fails, skip the character
                pass
        # Join the list of valid characters into a string and return it
        return ''.join(valid_chars)

    def save(self):

        try:
            page_data = self.page_data
            page_data['posts'] = self.posts
            # page_data['url'] = self.url
            page_data['createdAt'] = datetime.now().strftime('%Y-%m-%d')
            page_data['hasStat'] = "1"
            

            # e_name = re.sub(r'[^a-zA-Z0-9\s]+', '',
            #                     page_data.pop('name')).replace(' ', '_')
            

            e_name = page_data['name']
            print(f'e_name {e_name}')

            output_file = f"{self.env}_{self.establishment}_{e_name}_{datetime.now().strftime('%Y-%m-%d')}"

            print("posting ...")
            data = page_data.copy()
            print(data)
            data['posts'] = len(data['posts'])
            # del data['url']
            del data['name']
            data['post_items'] = data['posts']

            post = ERApi(method='postmulti', env=self.env)

            post.set_body(data)

            result = post.execute()

            print(result.text)

            print('saved')

            with open(f"{environ.get('SOCIAL_FOLDER')}/{output_file}.json", 'w') as foutput:
                json.dump(page_data, foutput, indent=4, sort_keys=True)

                self.posts = []
                self.page_data = {}

                return output_file

        except Exception as e:
            print("Erreur ici")
            print(e)

    def stop(self):
        pass
