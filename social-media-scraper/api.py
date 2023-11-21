import requests
import json
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

        if self.method == 'postmulti':

            url = f'{self.api_url}social/multi'
            files = []

            response = requests.request(
                "POST", url, headers=self.headers, params=self.params, data=json.dumps(self.body), files=files, verify=False)

            if response.status_code != 200:
                raise response.raise_for_status()

            return response

        else:
            self.add_header({"Content-Type": "application/json"})
            response = getattr(requests, self.method)(
                f'{self.api_url}{self.entity}',
                params=self.params,
                headers=self.headers,
                data=self.body,
                verify=False
            )

        return response and response.json()
