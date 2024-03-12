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

rating_structure = {
    'booking': [1, 2],
    'tripadvisor': [2, 1],
    'expedia': [2, 2],
    'campings': [1, 1],
    'trustpilot': [1, 1],
    'maeva': [1, 1],
    'hotels': [2, 2],
    'google': [1, 1],
    'opentable': [2, 1],
    'App (Private)': [1, 1]
}


class ReviewScore:

    def __init__(self):
        if os.environ.get('ENV_TYPE') == 'remote':
            self.model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.classifier = pipeline(
                'sentiment-analysis', model=self.model, tokenizer=self.tokenizer, device=-1)
        else:
            self.model_name = ""
            self.model = None
            self.tokenizer = None
            self.classifier = None

    def get_score(self, text):
        if self.classifier:
            # if lang in ['en', 'nl', 'de', 'fr', 'it', 'es']:
            try:
                return self.classifier(text.replace('\"', "\'"))
            except Exception as e:
                print(e)
                return False
        else:
            return False

    def compute_review_score(self, text, lang, rating, source):

        def compute_rating(rating, source):
            rate = 0
            rating_info = rating_structure[source]

            if rating_info[0] == 2:  # with /
                rate_tmp = rating.split('/')
                if rating_info[1] == 1:  # /5
                    rate = float(rate_tmp[0].replace(',', '.'))*2
                else:  # /10
                    rate = float(rate_tmp[0].replace(',', '.'))
            else:  # without /
                if rating_info[1] == 1:  # /5
                    rate = float(rating.replace(',', '.'))*2
                else:  # /10
                    rate = float(rating.replace(',', '.'))

            return rate/10

        rating = compute_rating(rating, source)

        if os.environ.get('ENV_TYPE') == 'local':
            return {'feeling': 'neutre', 'score': '0', 'confidence': '0'}
        else:
            score_data = self.get_score(text)

            if score_data:
                score_value = score_data[0]['score']
                score_label = score_data[0]['label']

                score_stars = int(score_label.split()[0])
                feeling = "negative" if score_stars < 3 else (
                    "positive" if score_stars > 3 else "neutre")

                if rating < 0.5:
                    if feeling == "neutre":
                        feeling = "negative"
                    elif feeling == "positive":
                        feeling = "neutre"
                elif rating == 0.5:
                    feeling = "neutre"
                else:
                    if rating >= 0.7:
                        feeling = "positive"
                    else:
                        if feeling == "negative":
                            feeling = "neutre"

                        elif feeling == "neutre":
                            feeling = "positive"
                        else:
                            feeling = "positive"

                if feeling == "negative":
                    score_value = (score_value + rating) / 2
                    confidence = -1 * score_value
                elif feeling == "neutre":
                    confidence = 0
                    score_value = 0
                else:
                    confidence = score_value = (score_value + rating) / 2

                return {'score': str(score_value), 'confidence': str(confidence), 'feeling': feeling}
            else:
                return {'score': '0', 'confidence': '0', 'feeling': "neutre"}

    def compute_comment_score(self, text):

        if os.environ.get('ENV_TYPE') == 'local':
            return {'feeling': 'neutre', 'score': '0', 'confidence': '0'}
        else:
            score_data = self.get_score(text)

            if score_data:
                score_value = score_data[0]['score']
                score_label = score_data[0]['label']

                score_stars = int(score_label.split()[0])
                feeling = "negative" if score_stars < 3 else (
                    "positive" if score_stars > 3 else "neutre")

                if feeling == "negative":
                    confidence = -1 * score_value
                elif feeling == "neutre":
                    confidence = 0
                    score_value = 0
                else:
                    confidence = score_value

                return {'score': str(score_value), 'confidence': str(confidence), 'feeling': feeling}
            else:
                return {'score': '0', 'confidence': '0', 'feeling': "neutre"}


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

    def __init__(self, env='dev', type='reviews', tag='', limit=5) -> None:
        self.type = type
        self.establishment = None
        self.categories = []
        self.tag = tag
        self.lines = []
        self.env = env
        self.limit = limit
        self.page = 1
        self.pages = 1

    def fetch_datas(self):
        try:
            get_instance = ERApi(
                method="get", entity=f"establishment/{self.tag}/reviews_to_classify", env=self.env, params={"type": self.type, "page": self.page, 'limit': self.limit})
            res = get_instance.execute()

            if (res):
                self.categories = res['categories']
                self.establishment = res['establishment']
                self.pages = res['pages']
                self.lines = res['reviews']
                print("Etablissement traité: ", res['establishment']['name'])
                print("Liste des catégories disponibles: ", res['categories'])
                print("Nombre total lignes à traiter: ", res['count'])

            self.page += 1

            # if len(self.categories):

            #     while (page <= pages):
            #         get_instance = ERApi(
            #             method="get", entity=f"establishment/{self.tag}/reviews_to_classify", env=self.env, params={'page': page, 'limit': self.limit})
            #         res = get_instance.execute()
            #         self.lines += res['reviews']
            #         page += 1
            #         time.sleep(1)

            print("Lignes récupérées: ", len(self.lines))

        except Exception as e:
            print(e)

    def compute_scores(self, comments):

        review_score = ReviewScore()

        def set_score(item):
            score_data = review_score.compute_comment_score(item['text']) if self.type == "comments" else review_score.compute_review_score(
                item['text'], item['language'], item['rating'], item['source'])

            item['feeling'] = score_data['feeling']
            item['score'] = score_data['score']
            item['confidence'] = score_data['confidence']

            return item

        return list(map(lambda x: set_score(x), comments))

    def check_categories(self, line):
        if os.environ.get('ENV_TYPE') == 'local':
            line['prediction'] = {
                # 'labels': ['travel', 'cooking', 'dancing'],
                'labels': self.categories,
                # 'scores': [random.uniform(0, 1) for i in range(3)],
                'scores': [random.uniform(0, 1) for i in range(len(self.categories))],
                'sequence': line['text']
            }
        else:
            if len(self.categories):
                try:
                    classifier = pipeline(task="zero-shot-classification",
                                          device=-1, model="facebook/bart-large-mnli")

                    prediction = classifier(
                        line['text'], list(map(lambda x: x['category'], self.categories)), multi_label=False)

                    # prediction = {
                    #     # 'labels': ['travel', 'cooking', 'dancing'],
                    #     'labels': self.categories,
                    #     # 'scores': [random.uniform(0, 1) for i in range(3)],
                    #     'scores': [random.uniform(0, 1) for i in range(len(self.categories))],
                    #     'sequence': line['text']
                    # }

                    line['prediction'] = prediction

                except Exception as e:
                    print(e)
                    line['prediction'] = None

            else:
                line['prediction'] = None

        return line

    def update_lines(self):
        for line in self.lines:
            if line['text'] != "":
                line = self.check_categories(line)

        self.lines = self.compute_scores(self.lines)

    def transform_data(self):

        result = ""
        for line in self.lines:
            l_categs = ""
            c_categs = ""

            [print(line['prediction']) if 'prediction' in line.keys()
             else print("no prediction found")]

            if 'prediction' in line.keys() and line['prediction']:
                for i in range(0, len(line['prediction']['labels'])):
                    if line['prediction']['scores'][i] >= 0.9:
                        l_categs += f"{line['prediction']['labels'][i]}${str(line['prediction']['scores'][i])}|"

            if len(self.categories):
                c_categs = "|".join(
                    list(map(lambda x: x['category'], self.categories)))

            l = "&".join([str(line['id']), self.type, line['feeling'],
                         str(line['score']), str(line['confidence']), l_categs, c_categs])
            result += l + "#"

        return result

    def upload(self):
        try:
            data = self.transform_data()
            print(data)
            # post_instance = ERApi(
            #     method="postclassifications", entity=f"classification/multi", env=self.env, body={'data_content': data})
            # return post_instance.execute()
        except Exception as e:
            print(e)

    def execute(self):
        try:
            while (True):
                print("============> Page ", self.page,
                      "sur ", self.pages, " <===============")
                self.fetch_datas()
                if len(self.categories):
                    self.update_lines()
                # res = self.transform_data()
                # print(res)
                    res = self.upload()
                    print(res)
                else:
                    print("!!!! Pas de catégories")
                    break

                if self.page > self.pages:
                    break
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
                print("======> Etablissement: ",
                      item['name'], ' <========')
                cl = ClassificationAPI(
                    tag=item['tag'], type=args.type, limit=20, env=args.env)
                cl.execute()

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
