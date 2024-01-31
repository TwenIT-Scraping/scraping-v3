import csv
import pprint
import json
import random
import pandas as pd
from datetime import datetime, timedelta
from random import randint
import sys
import os
import time
from abc import abstractmethod
import orjson
import dotenv
import argparse
import ssl
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from api import ERApi

dotenv.load_dotenv()


def main_arguments() -> object:
    parser = argparse.ArgumentParser(description="Programme catégorisation",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--type', '-t', dest='type', default='',
                        help="""Options: comment, review""")
    parser.add_argument('--env', '-v', dest='env', default="DEV",
                        help="Optionnel: environnement de l'api. DEV par défaut")
    parser.add_argument('--names', '-n', dest='names',
                        help="Nom des établissements à traiter, séparé par des virgules.")
    return parser.parse_args()


ARGS_INFO = {
    '-t': {'long': '--type', 'dest': 'type', 'help': "Options: comment, review"},
    '-v': {'long': '--env', 'dest': 'env', 'help': "Optionnel: environnement de l'api. PROD par défaut"},
    '-n': {'long': '--names', 'dest': 'names', 'help': "Nom des établissements à traiter, séparé par des virgules."}
}


class ClassificationAPI(object):

    def __init__(self, env='dev', type='review', tag='', limit=50) -> None:
        self.type = type
        self.establishment = None
        self.categories = []
        self.tag = tag
        self.lines = []
        self.env = env
        self.limit = limit

    def fetch_datas(self):
        try:
            get_instance = ERApi(
                method="get", entity=f"establishment/{self.tag}/reviews_to_classify", env=self.env, params={'limit': self.limit})
            res = get_instance.execute()
            pages = 1
            page = 2

            if (res):
                self.categories = res['categories']
                self.establishment = res['establishment']
                pages = res['pages']
                self.lines = res['reviews']
                print("Etablissement traité: ", res['establishment']['name'])
                print("Liste des catégories disponibles: ", res['categories'])
                print("Nombre total lignes à traiter: ", res['count'])

            if len(self.categories):

                while (page <= pages):
                    get_instance = ERApi(
                        method="get", entity=f"establishment/{self.tag}/reviews_to_classify", env=self.env, params={'page': page, 'limit': self.limit})
                    res = get_instance.execute()
                    self.lines += res['reviews']
                    page += 1
                    time.sleep(1)

                print("Lignes récupérées: ", len(self.lines))

        except Exception as e:
            print(e)

    def check_categories(self, line):
        try:
            # classifier = pipeline(task="zero-shot-classification",
            #                       device=0, model="facebook/bart-large-mnli")

            # prediction = classifier(
            #     line['text'], self.categories, multi_class=False)

            prediction = {
                # 'labels': ['travel', 'cooking', 'dancing'],
                'labels': self.categories,
                # 'scores': [random.uniform(0, 1) for i in range(3)],
                'scores': [random.uniform(0, 1) for i in range(len(self.categories))],
                'sequence': line['text']
            }

            line['prediction'] = prediction

            return line

        except Exception as e:
            print(e)

    def update_lines(self):
        for line in self.lines:
            line = self.check_categories(line)

    def transform_data(self):
        result = ""
        for line in self.lines:
            for i in range(0, len(line['prediction']['labels'])):
                if line['prediction']['scores'][i] >= 0.9:
                    result += f"{self.type}&{line['prediction']['labels'][i]['category']}&{line['prediction']['scores'][i]}&{line['id']}#"

        return result

    def upload(self):
        try:
            data = self.transform_data()
            post_instance = ERApi(
                method="postclassifications", entity=f"classification/multi", env=self.env, body={'data_content': data})
            return post_instance.execute()
        except Exception as e:
            print(e)

    def execute(self):
        try:
            self.fetch_datas()
            if len(self.categories):
                self.update_lines()
                # res = self.transform_data()
                res = self.upload()
                print(res)
            else:
                print("!!!! Pas de catégories")
        except Exception as e:
            print(e)


def check_arguments(args):
    miss = []
    if not getattr(args, ARGS_INFO['-t']['dest']):
        miss.append(
            f'-t ou {ARGS_INFO["-t"]["long"]} ({ARGS_INFO["-t"]["help"]})')

    return miss


if __name__ == '__main__':

    history_filename = f'{os.environ.get("HISTORY_FOLDER")}/categorisation/categorisation-scraping-log.txt'

    if not os.path.exists(f'{os.environ.get("HISTORY_FOLDER")}/categorisation'):
        os.mkdir(f'{os.environ.get("HISTORY_FOLDER")}/categorisation')

    now = datetime.now()
    if os.path.exists(history_filename):
        with open(history_filename, 'a', encoding='utf-8') as file:
            file.write("Démarrage catégorisation: " +
                       now.strftime("%d/%m/%Y %H:%M:%S"))
    else:
        with open(history_filename, 'w', encoding='utf-8') as file:
            file.write("Démarrage catégorisation: " +
                       now.strftime("%d/%m/%Y %H:%M:%S"))

    args = main_arguments()

    miss = check_arguments(args)

    if not len(miss):

        try:
            datetime_now = datetime.now().strftime("%Y-%m-%d %H_%M")

            get_instance = ERApi(
                method="get", entity=f"establishment/name", env=args.env)
            all_establishments = get_instance.execute()
            todo = []

            if args.names:
                todo = [item for item in all_establishments if item['name']
                        in args.names.split(',')]
            else:
                todo = all_establishments

            for item in todo:
                if args.type == "reviews":
                    print("======> Etablissement: ",
                          item['name'], ' <========')
                    cl = ClassificationAPI(tag=item['tag'])
                    cl.execute()
            # if args.type == "reviews":
            #     cl = ClassificationAPI(tag="645de52f135e8")
            #     cl.execute()

        except Exception as e:
            now = datetime.now()
            with open(history_filename, 'a', encoding='utf-8') as file:
                file.write("  ===>  Fin catégorisation AVEC ERREURS: " +
                           now.strftime("%d/%m/%Y %H:%M:%S") + ':' + str(e) + '\n')

        now = datetime.now()

        with open(history_filename, 'a', encoding='utf-8') as file:
            file.write("  ===>  Fin catégorisation: " +
                       now.strftime("%d/%m/%Y %H:%M:%S") + '\n')

    else:
        now = datetime.now()
        with open(history_filename, 'a', encoding='utf-8') as file:
            file.write("  ===>  Fin catégorisation AVEC ERREURS: " +
                       now.strftime("%d/%m/%Y %H:%M:%S") + ':' + f"Argument(s) manquant(s): {', '.join(miss)}" + '\n')
