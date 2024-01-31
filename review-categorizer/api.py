import requests
import json
from tkinter import messagebox
from datetime import datetime
import shutil
import dotenv
import os
from urllib3 import encode_multipart_formdata


class ERApi:

    def __init__(self, env, method="get", entity="", params={}, body={}, id=-1):
        dotenv.load_dotenv()

        self.method = method
        self.entity = entity
        token = os.environ.get(f'API_TOKEN_{env.upper()}')
        self.headers = {'Accept': 'application/json', 'Authorization': token}
        self.params = params
        self.body = body
        self.id = id
        self.api_url = os.environ.get(f"API_URL_{env.upper()}")
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

        elif self.method == 'postclassifications':

            url = f'{self.api_url}classification/multi'
            self.add_header({"Content-Type": "application/json"})
            headers = self.headers

            response = requests.request(
                "POST", url, headers=headers, data=json.dumps(self.body), verify=False)

            if response:
                if response.text:
                    print(response.text)

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
