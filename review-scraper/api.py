import requests
import json
from tkinter import messagebox
from datetime import datetime
import shutil
import dotenv
import os
from urllib3 import encode_multipart_formdata


class ERApi:

    def __init__(self, method="get", entity="", params={}, body={}, id=-1):
        dotenv.load_dotenv()

        self.method = method
        self.entity = entity
        token = os.environ.get('API_TOKEN')
        self.headers = {'Accept': 'application/json', 'Authorization': token}
        self.params = params
        self.body = body
        self.id = id
        self.api_url = os.environ.get("API_URL")
        self.media_dir = os.environ.get("MEDIA_DIR")

    def set_id(self, id):
        self.id = id

    def set_body(self, body):
        self.body = body

    def set_entity(self, entity):
        self.entity = entity

    def add_file(self, files):
        self.files = files

    def add_header(self, header):
        for key in header.keys():
            self.headers[key] = header[key]

    def add_params(self, param):
        for key in param.keys():
            self.params[key] = param[key]

    def execute(self):
        response = {}
        if self.method == 'delete':
            if self.id != -1:
                response = getattr(requests, self.method)(
                    f'{self.api_url}{self.entity}/{self.id}',
                    params=self.params,
                    headers=self.headers
                )
                return response
            else:
                messagebox.askyesno(
                    "Information", "Identifiant non spécifié!!!")

        elif self.method == 'patch' or self.method == 'put':
            if self.id != -1:
                self.add_header({"Content-Type": "application/json"})
                response = getattr(requests, self.method)(
                    f'{self.api_url}{self.entity}/{self.id}',
                    params=self.params,
                    headers=self.headers,
                    data=json.dumps(self.body)
                )
                return response
            else:
                messagebox.askyesno(
                    "Information", "Identifiant non spécifié!!!")

        elif self.method == 'getone':
            if self.id != -1:
                response = getattr(requests, 'get')(
                    f'{self.api_url}{self.entity}/{self.id}',
                    params=self.params,
                    headers=self.headers
                )
            else:
                messagebox.askyesno(
                    "Information", "Identifiant non spécifié!!!")

        elif self.method == 'postmulti':

            url = f'{self.api_url}reviews/multi'
            self.add_header({"Content-Type": "application/json"})
            headers = self.headers

            response = requests.request(
                "POST", url, headers=headers, data=json.dumps(self.body), verify=False)

            if response:
                print(response.json())

                return response

        else:
            self.add_header({"Content-Type": "application/json"})
            response = getattr(requests, self.method)(
                f'{self.api_url}{self.entity}',
                params=self.params,
                headers=self.headers,
                data=json.dumps(self.body),
                verify=False
            )

        if response.status_code >= 400:
            response.raise_for_status()

        return response and response.json()

    def upload_media(self, url_source, parent_entity, parent_id, site):
        try:
            fields = {
                "source": site,
                f'{parent_entity}': parent_id,
                'url_source': url_source,
                'use_local_file': True
            }
            body, header = encode_multipart_formdata(fields)
            self.set_body(body)
            self.add_header({
                'Content-Type': header
            })
            self.set_entity("media")
            self.execute()
            print("Media uploaded successfully")

        except Exception as e:
            print(e)
            pass

    @staticmethod
    def delete_multi(entity, ids):
        delete_instance = ERApi("delete", entity)
        for item in ids:
            delete_instance.set_id(item)
            try:
                r = delete_instance.execute()
            except:
                pass

    @staticmethod
    def get_all(entity):
        all_data = []
        page = 1

        while True:
            getreq = ERApi('get', entity)
            getreq.add_params({'page': page})
            results = getreq.execute()
            all_data += results
            page += 1
            if len(results) == 0:
                break

        return all_data

    @staticmethod
    def delete_all(entity):
        all_ids = [item['id'] for item in ERApi.get_all(entity)]
        delete_req = ERApi(method="delete", entity=entity)
        for item in all_ids:
            delete_req.set_id(item)
            delete_req.execute()

    @staticmethod
    def load_json(filename):
        with open(filename) as json_file:
            data = json.load(json_file)
            return data

    @staticmethod
    def save_media(filename, source):
        with open(filename, 'wb') as f:
            source.raw.decode_content = True
            shutil.copyfileobj(source.raw, f)
            print('Image Downloaded Successfully')
            return filename

    @staticmethod
    def post_multi(entity, p_list, website):
        post_instance = ERApi("post", entity)
        post_instance.add_header({"Content-Type": "application/json"})
        for item in p_list:
            reviews = []
            if 'reviews' in item.keys():
                reviews = item.pop('reviews')

            if 'images' in item.keys():
                images = item.pop('images')

            print("Ici")

            post_instance.set_body(item)
            r = post_instance.execute()

            if len(reviews) > 0:
                post_child = ERApi("post", 'reviews')
                post_child.add_header({"Content-Type": "application/json"})
                for v in reviews:
                    v[f'{entity[:-1]}'] = f"/api/{entity}/{r['id']}"
                    post_child.set_body(v)
                    try:
                        post_child.execute()
                    except:
                        pass

        return True
