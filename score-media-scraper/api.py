import requests
import json
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
        response = None

        if self.method == 'postmulti':

            url = f'{self.api_url}social/multi'

            try:

                response = requests.request(
                    "POST", url, headers=self.headers, data=json.dumps(self.body), verify=False)

                if response.status_code != 200:
                    raise response.raise_for_status()

                print(response.json())

                return response
            except Exception as e:
                print(e)

        else:
            try:
                self.add_header({"Content-Type": "application/json"})
                response = getattr(requests, self.method)(
                    f'{self.api_url}{self.entity}',
                    params=self.params,
                    headers=self.headers,
                    data=self.body,
                    verify=False
                )
                if response.status_code in ['200','201']:
                    print('REPONSE OK DU SERVEUR CONCERNANT LA REQUETE (bien envoyé)') 
                    
                print(response.text)
            except Exception as e:
                print(e)

        return response and response.json()
