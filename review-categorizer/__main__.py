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
from progress.bar import ChargingBar
from progress.spinner import Spinner
from checkclassifier import ia_categorize, classify_text
from checkclassifier_v2 import ia_categorize_v2, set_global_config, ia_sentiment_analysis_v2

dotenv.load_dotenv()

rating_structure = {
    'booking': [1, 2],
    'tripadvisor': [2, 1],
    'expedia': [2, 2],
    'campings': [1, 2],
    'trustpilot': [1, 1],
    'maeva': [1, 1],
    'hotels': [2, 2],
    'google': [1, 1],
    'opentable': [2, 1],
    'App (Private)': [1, 1]
}

type_dict = {
    'reviews': 'review',
    'posts': 'socialPost',
    'comments': 'socialComment'
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
            print("classifier not initiated!!!")
            return False

    def compute_review_score(self, text, lang, rating, source):

        def compute_rating(rating, source):
            rate = 0
            rating_info = rating_structure[source]

            try:
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
            except:
                if '/' in rating:
                    rate_tmp = rating.split('/')
                    if rate_tmp[1] == '5':  # /5
                        rate = float(rate_tmp[0].replace(',', '.'))*2
                    else:  # /10
                        rate = float(rate_tmp[0].replace(',', '.'))

            return rate/10

        rating = compute_rating(rating, source)

        if os.environ.get('ENV_TYPE') == 'local':
            return {'feeling': None, 'score': None, 'confidence': None}
        else:
            score_data = self.get_score(text)

            if score_data:
                confidence = score_data[0]['score']
                score_value = confidence
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
                    if score_stars == 1:
                        score_value = -1*confidence
                    if score_stars == 2:
                        score_value = -0.75
                elif feeling == "neutre":
                    score_value = 0
                else:
                    if score_stars == 4:
                        score_value = 0.75
                    if score_stars == 5:
                        score_value = confidence

                return {'score': str(score_value), 'confidence': str(confidence), 'feeling': feeling}
            else:
                return {'score': None, 'confidence': None, 'feeling': None}

    def compute_comment_score(self, text):

        if os.environ.get('ENV_TYPE') == 'local':
            return {'feeling': None, 'score': None, 'confidence': None}
        else:
            score_data = self.get_score(text)

            if score_data:
                confidence = score_data[0]['score']
                score_value = confidence
                score_label = score_data[0]['label']

                score_stars = int(score_label.split()[0])
                feeling = "negative" if score_stars < 3 else (
                    "positive" if score_stars > 3 else "neutre")

                if feeling == "negative":
                    if score_stars == 1:
                        score_value = -1*confidence
                    if score_stars == 2:
                        score_value = -0.75
                elif feeling == "neutre":
                    score_value = 0
                else:
                    if score_stars == 4:
                        score_value = 0.75
                    if score_stars == 5:
                        score_value = confidence

                return {'score': str(score_value), 'confidence': str(confidence), 'feeling': feeling}
            else:
                return {'score': None, 'confidence': None, 'feeling': None}


class ClassificationAPI(object):

    def __init__(self, env='dev', type='reviews', tag='', limit=5, column="category") -> None:
        self.type = type
        self.establishment = None
        self.categories = []
        self.tag = tag
        self.lines = []
        self.env = env
        self.limit = limit
        self.page = 1
        self.pages = 1
        self.column = column

    def fetch_datas(self):
        endpoint = f"establishment/{self.tag}/reviews_to_classify" if self.column == "category" else f"establishment/{self.tag}/reviews_to_score"

        try:
            get_instance = ERApi(
                method="get", entity=endpoint, env=self.env, params={"all": "yes", "type": self.type, "page": self.page, 'limit': self.limit})
            res = get_instance.execute()

            if (res):
                print("Etablissement trait�: ", res['establishment']['name'])

                if self.column == "category":
                    print("Liste des cat�gories disponibles: ",
                          res['categories'])
                    self.categories = res['categories']

                self.establishment = res['establishment']
                self.pages = res['pages']
                self.lines = res['reviews']

                print(
                    f"Lignes trait�es: {(self.page-1)*self.limit}/{res['count']}")

            self.page += 1

            print("Lignes r�cup�r�es: ", len(self.lines))

        except Exception as e:
            print(e)

    def check_results(self):
        results = []
        stats = {'categories': [], 'classification': {},
                 'nocategorized': [], 'classified': 0}
        page = 1

        print("Fetching data ...")

        while (True):
            endpoint = f"review/by_establishment?tag={self.tag}&page={page}&limit=200&from=2023-09-01&to=2024-05-22"
            try:
                get_instance = ERApi(
                    method="get", entity=endpoint, env=self.env, params={"all": "yes", "type": self.type, "page": self.page, 'limit': self.limit})
                res = get_instance.execute()

                if not res or not res['data'] or len(res['data']) == 0:
                    break
                else:
                    results += res['data']

                page += 1

            except:
                break

        for line in results:
            if line['category']:
                categories = line['category'].split(';')

                if len(categories):

                    for categ in categories:
                        if categ not in stats['categories']:
                            stats['categories'].append(categ)

                        if categ not in stats['classification'].keys():
                            stats['classification'][categ] = []

                        stats['classification'][categ].append({
                            'id': line['id'],
                            'type': 'review',
                            'category_check': line['category_check'],
                        })

                        stats['classified'] = stats['classified'] + 1

                else:
                    stats['nocategorized'].append({
                        'id': line['id'],
                        'type': 'review',
                        'category_check': line['category_check'],
                    })
            else:
                stats['nocategorized'].append({
                    'id': line['id'],
                    'type': 'review',
                    'category_check': line['category_check'],
                })

        print("\n================ RESULTATS ==================\n")
        print("Nombre total reviews: ", len(results))
        print("Cat�gories:", stats['categories'])
        print("Nombre reviews classifi�s: ", stats['classified'])
        print("Nombre reviews non classifi�s: ", len(stats['nocategorized']))
        print("Reviews par cat�gorie: ")

        for categ in stats['classification'].keys():
            print("\t", categ, ":", len(stats['classification'][categ]))

        print("\n=============================================\n")

    def compute_scores(self, comments):

        review_score = ReviewScore()

        def set_score(item):
            score_data = {}

            if self.type == "comments":
                score_data = review_score.compute_comment_score(item['text'])
            elif self.type == "posts":
                score_data = review_score.compute_comment_score(item['text'])
            else:
                score_data = review_score.compute_review_score(
                    item['text'], item['language'], item['rating'], item['source'])

            item['feeling'] = score_data['feeling']
            item['score'] = score_data['score']
            item['confidence'] = score_data['confidence']

            return item

        results = []

        progress = ChargingBar('Calcul scores: ', max=len(comments))
        for item in comments:
            if item['text'] and len(item['text']) > 0:
                results.append(set_score(item))
                progress.next()

        return results

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

                categs = list(
                    map(lambda x: x['category'], self.categories))

                line['prediction'] = classify_text(categs, line['text'])

            else:
                line['prediction'] = None

        return line

    def update_lines(self):
        if self.column == "category":
            progress = ChargingBar(
                'Calcul cat�gorisation', max=len(self.lines))
            for i in range(len(self.lines)):
                progress.next()
                line = self.lines[i]

                if line['text'] != "" and len(line['text']) >= 25:
                    self.lines[i] = self.check_categories(line)

        if self.column == "feeling":
            self.lines = self.compute_scores(self.lines)

    def transform_data(self):

        result = ""

        if self.column == "feeling":

            print("Transformation ...")

            for line in self.lines:

                l = "&".join([str(line['id']), self.type, line['feeling'],
                              str(line['score']), str(line['confidence'])])
                result += l + "#"

        if self.column == "category":

            print("\n******** Cat�gories trouv�es *********\n")

            for line in self.lines:
                l_categs = ""
                c_categs = ""

                if 'prediction' in line.keys() and line['prediction']:
                    for i in range(0, len(line['prediction']['labels'])):
                        if line['prediction']['scores'][i] >= 0.8 and len(f"{line['prediction']['sequence']}") > 30:
                            l_categs += f"{line['prediction']['labels'][i]}${str(line['prediction']['scores'][i])}|"

                if len(self.categories):
                    c_categs = "|".join(
                        list(map(lambda x: x['category'], self.categories)))

                l_categs != "" and print(
                    f"- {l_categs.replace('|', ', ')} => {line['prediction']['sequence']}\n")

                l = "&".join([str(line['id']), self.type, l_categs, c_categs])
                result += l + "#"

            print("\n**************************************\n")

        return result

    def upload(self):
        try:
            data = self.transform_data()

            print(data)

            endpoint = "classification/multi" if self.column == "category" else "feeling/multi"
            # print(data)
            post_instance = ERApi(
                method="postclassifications", entity=endpoint, env=self.env, body={'data_content': data})
            return post_instance.execute()
        except Exception as e:
            print(e)

    def execute(self):
        try:
            while (True):
                print("============> Page ", self.page,
                      "sur ", self.pages, " <===============")
                self.fetch_datas()
                if self.column == "category":
                    if len(self.categories):
                        self.update_lines()
                        # res = self.transform_data()
                        # print(res)

                    else:
                        print("!!!! Pas de cat�gories")
                        break
                else:
                    self.update_lines()

                if os.environ.get('ENV_TYPE') != 'local':
                    res = self.upload()
                    print(res)

                print(len(self.lines))

                if self.page > self.pages:
                    break
        except Exception as e:
            print(e)


class ClassificationAPIV2(object):

    def __init__(self, env='dev', type='reviews', tag='', limit=5, column="category", language='en', full_text='Y') -> None:
        self.type = type
        self.establishment = None
        self.categories = []
        self.tag = tag
        self.lines = []
        self.env = env
        self.limit = limit
        self.page = 1
        self.pages = 1
        self.column = column
        self.language = language
        self.full_text = full_text

        set_global_config(os.environ.get(
            f"API_URL_{env.upper()}"), os.environ.get(f'API_TOKEN_{env.upper()}'))

    def check_results(self):
        results = []
        stats = {'categories': [], 'classification': {},
                 'nocategorized': [], 'classified': 0}
        page = 1

        print("Fetching data ...")

        while (True):
            endpoint = f"review/by_establishment?tag={self.tag}&page={page}&limit=200&from=2023-09-01&to=2024-05-22"
            try:
                get_instance = ERApi(
                    method="get", entity=endpoint, env=self.env, params={"all": "yes", "type": self.type, "page": self.page, 'limit': self.limit})
                res = get_instance.execute()

                if not res or not res['data'] or len(res['data']) == 0:
                    break
                else:
                    results.extend(res['data'])

                page += 1

            except:
                break

        for line in results:
            if line['category']:
                categories = line['category'].split(';')

                if len(categories):

                    for categ in categories:
                        if categ not in stats['categories']:
                            stats['categories'].append(categ)

                        if categ not in stats['classification'].keys():
                            stats['classification'][categ] = []

                        stats['classification'][categ].append({
                            'id': line['id'],
                            'type': 'review',
                            'category_check': line['category_check'],
                        })

                        stats['classified'] = stats['classified'] + 1

                else:
                    stats['nocategorized'].append({
                        'id': line['id'],
                        'type': 'review',
                        'category_check': line['category_check'],
                    })
            else:
                stats['nocategorized'].append({
                    'id': line['id'],
                    'type': 'review',
                    'category_check': line['category_check'],
                })

        print("\n================ RESULTATS ==================\n")
        print("Nombre total reviews: ", len(results))
        print("Cat�gories:", stats['categories'])
        print("Nombre reviews classifi�s: ", stats['classified'])
        print("Nombre reviews non classifi�s: ", len(stats['nocategorized']))
        print("Reviews par cat�gorie: ")

        for categ in stats['classification'].keys():
            print("\t", categ, ":", len(stats['classification'][categ]))

        print("\n=============================================\n")

    def execute(self):
        results = []
        is_done = False

        try:
            while (True):
                # print("============> Page ", self.page,
                #       "sur ", self.pages, " <===============")

                if self.column == "category":
                    is_done = ia_categorize_v2(
                        self.tag, self.type, self.language, self.page)
                else:
                    is_done = ia_sentiment_analysis_v2(
                        self.tag, self.full_text == 'Y', self.page)

                if is_done:
                    break
                else:
                    self.page += 1

        except Exception as e:
            print(e)

        return results


def main_arguments() -> object:
    parser = argparse.ArgumentParser(description="Programme cat�gorisation",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--type', '-t', dest='type', default='reviews',
                        help="""Options: comments, reviews""")
    parser.add_argument('--env', '-v', dest='env', default="DEV",
                        help="Optionnel: environnement de l'api. DEV par d�faut")
    parser.add_argument('--names', '-n', dest='names',
                        help="Nom des �tablissements � traiter, s�par� par des virgules.")
    parser.add_argument('--column', '-c', dest='column',
                        help="Option: feeling, category", default="category")
    parser.add_argument('--language', '-l', dest='language',
                        help="Option: en, fr, es", default="fr")
    parser.add_argument('--results', '-r', dest='stat',
                        default="N", help="Option: N ou Y")
    parser.add_argument('--full', '-f', dest='full_text', default="Y",
                        help="Option: Y si texte complet et N si par section")
    return parser.parse_args()


ARGS_INFO = {
    '-t': {'long': '--type', 'dest': 'type', 'help': "Options: comments, reviews, posts. reviews par d�faut."},
    '-c': {'long': '--column', 'dest': 'column', 'help': "Options: feeling, category. category par d�faut."},
    '-v': {'long': '--env', 'dest': 'env', 'help': "Optionnel: environnement de l'api. PROD par d�faut"},
    '-n': {'long': '--names', 'dest': 'names', 'help': "Nom des �tablissements � traiter, s�par� par des virgules."},
    '-r': {'long': '--results', 'dest': 'stat', 'help': 'Option: N ou Y'},
    '-l': {'long': '--language', 'dest': 'language', 'help': 'Option: en, fr ou es'},
    '-f': {'long': '--full', 'dest': 'full_text', 'help': 'Option: Y si texte complet et N si par section'}
}


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
            file.write("D�marrage cat�gorisation: " +
                       now.strftime("%d/%m/%Y %H:%M:%S"))
    else:
        with open(history_filename, 'w', encoding='utf-8') as file:
            file.write("D�marrage cat�gorisation: " +
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

            print("Initialement: ", len(all_establishments))

            if args.names:
                todo = [item for item in all_establishments if item['name']
                        in args.names.split(',') and item['customer_id']]
            else:
                todo = [item for item in all_establishments if item['customer_id']]

            print("Avant second filtre:")

            [print(item['name']) for item in todo]

            final_todo = []

            print(todo)

            for item in todo:
                if item['language'] and item['language'] == args.language:
                    final_todo.append(item)

                else:
                    final_todo.append(item)

            print("Apres second filtre: ", len(final_todo))

            [print(item['name']) for item in todo]

            # [print(item['name'], item['tag']) for item in final_todo]

            all_results = []

            for item in final_todo:
                try:
                    print("======> Etablissement: ",
                          item['name'], ' <========')
                    cl = ClassificationAPIV2(
                        tag=item['tag'], type=args.type, limit=20, env=args.env, column=args.column, language=args.language, full_text=args.full_text)

                    if args.stat == 'Y':
                        cl.check_results()
                    else:
                        cl.execute()
                except Exception as e:
                    print(e)

        except Exception as e:
            now = datetime.now()
            with open(history_filename, 'a', encoding='utf-8') as file:
                file.write("  ===>  Fin cat�gorisation AVEC ERREURS: " +
                           now.strftime("%d/%m/%Y %H:%M:%S") + ':' + str(e) + '\n')

        now = datetime.now()

        with open(history_filename, 'a', encoding='utf-8') as file:
            file.write("  ===>  Fin cat�gorisation: " +
                       now.strftime("%d/%m/%Y %H:%M:%S") + '\n')

    else:
        now = datetime.now()
        with open(history_filename, 'a', encoding='utf-8') as file:
            file.write("  ===>  Fin cat�gorisation AVEC ERREURS: " +
                       now.strftime("%d/%m/%Y %H:%M:%S") + ':' + f"Argument(s) manquant(s): {', '.join(miss)}" + '\n')
