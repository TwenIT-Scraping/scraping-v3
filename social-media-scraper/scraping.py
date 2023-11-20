import json
from os import path, environ
from api import ERApi
import dotenv

dotenv.load_dotenv()


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
        def format_postbody():
            column_order = ['title', 'publishedAt',
                            'likes', 'share', 'comments']

            def check_value(item):
                for key in column_order:
                    if not item[key] or item[key] == '':
                        return False
                return True

            results = ""

            for item in self.posts:
                print(item)
                # if check_value(item):
                # print("Checked !!!")
                line = '|&|'.join([item['title'], item['publishedAt'],
                                   str(item['likes']), str(item['share']), str(item['comments'])]) + "|*|"
                if len(line.split('|&|')) == 5:
                    results += line

            return results

        print(self.page_data)
        print(len(self.posts))
        print(self.posts)
        print()
        print()

        page_data = self.page_data
        # page_data.pop('name')
        page_data['posts'] = self.posts
        page_data['url'] = self.url

        with open(f"{environ.get('HISTORY_FOLDER')}/{page_data.pop('name')}.json", 'w') as foutput:
            json.dump(page_data, foutput, indent=4, sort_keys=True)
        # datas = format_postbody()

        # print(page_data)
        # print('\n')
        # print(datas)

        # post = ERApi(method='postmulti')
        # post.add_params(page_data)

        # print(datas)

        # post.set_body({'post_items': datas})

        # post.execute()

        self.posts = []
        self.page_data = {}

    def stop(self):
        pass


def format_jsondata(input, output):
    column_order = ['title', 'publishedAt',
                    'likes', 'share', 'comments']

    def check_value(item):
        for key in column_order:
            if not item[key] or item[key] == '':
                return False
        return True

    results = ""
    datas = []

    with open(input, 'r') as finput:
        datas = json.load(finput)

    for item in datas:
        print("Checked !!!")
        line = '|&|'.join([item['title'], item['uploadAt'],
                           str(0), str(item['share']), str(item['comments'])]) + "|*|"
        print(line)
        if len(line.split('|&|')) == 5:
            results += line


# format_jsondata('fb_data.json', 'fb_data.txt')
