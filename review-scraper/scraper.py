from models import Establishment, Settings
# from booking import Booking
from maeva import Maeva
from campings import Campings
# from hotels import Hotels_FR, Hotels_EN
from googles import Google
from opentable import Opentable, Opentable_UK
from trustpilot import Trustpilot
from tripadvisor import Tripadvisor_UK, Tripadvisor_FR
from expedia import Expedia
from api import ERApi
import random
from changeip import refresh_connection
import time
from datetime import datetime
# from tools import ReviewScore


__class_name__ = {
    # 'booking': Booking,
    # 'Booking ES': Booking,
    'maeva': Maeva,
    'camping': Campings,
    # 'hotels_com': Hotels_FR,
    'google': Google,
    'opentable': Opentable,
    'trustpilot': Trustpilot,
    'tripadvisor': Tripadvisor_UK,
    'expedia': Expedia
}

__class_name_v2__ = {
    # 'Booking': Booking,
    # 'Booking ES': Booking,
    'Maeva': Maeva,
    'Maeva ES': Maeva,
    'Campings': Campings,
    'Campings ES': Campings,
    # 'Hotels.com FR': Hotels_FR,
    # 'Hotels.com ES': Hotels_FR,
    'Google': Google,
    'Google hotel': Google,
    'Google Travel': Google,
    'Opentable UK': Opentable_UK,
    'Opentable': Opentable,
    'Trustpilot': Trustpilot,
    'Tripadvisor FR': Tripadvisor_FR,
    'Tripadvisor UK': Tripadvisor_UK,
    'Tripadvisor ES': Tripadvisor_UK,
    'Expedia': Expedia,
    'Expedia FR': Expedia,
    'Expedia ES': Expedia,
}


class ListScraper:
    def __init__(self,):
        self.establishments = []
        self.ids = []

    def init(self, establishments=[]):
        instance = ERApi(entity="establishment/name", env="PROD")
        etabs = instance.execute()
        if len(establishments):
            self.ids = list(map(lambda y: y, list(
                filter(lambda x: x['name'] in establishments, etabs))))
        else:
            self.ids = list(
                map(lambda x: x, etabs))

        for item in self.ids:
            print("Récupération information des établissements: ",
                  self.ids.index(item)+1, '/', len(self.ids))
            etab = Establishment(rid=item['id'], name=item['name'])
            etab.set_tag(item['tag'])
            etab.refresh()
            self.establishments.append(etab)

    def start(self, websites=[]):
        refresh_connection()

        counter = 0

        for item in self.establishments:
            time.sleep(random.randint(1, 5))

            print("****** Establishment: ", item.name, " ******")

            for site in item.websites.keys():
                if site in websites:
                    if site in __class_name__.keys():
                        print("===>\t", site)
                        instance = __class_name__[site](
                            url=item.websites[site], establishment=item.id)
                        instance.execute()
                        print("\n\n")
                        counter += 1

                        if counter == 4:
                            counter == 0
                            refresh_connection()


class ListScraperV2:
    def __init__(self, env):
        self.settings = None
        self.last_date = None
        self.env = env
        print(self.env)

    def get_providers(self):
        res = ERApi(entity='providers', env=self.env).execute()
        return list(map(lambda x: {'name': x['name'], 'count': len(x['settings'])}, res))

    def init(self, eid=None, ename=None, categ=None, source=None):
        self.settings = Settings(categ, eid, source, ename, self.env)
        self.settings.prepare()

    def get_comments(self, page):
        commentsApi = ERApi(entity='review/feeling_null',
                            params={'page': page, 'limit': 50}, env=self.env)
        return commentsApi.execute()['data']

    # def compute_scores(self, comments):
    #     review_score = ReviewScore()

    #     def set_score(item):
    #         score_data = review_score.compute_score(
    #             item['comment'], item['language'], item['rating'], item['source'])

    #         item['feeling'] = score_data['feeling']
    #         item['score'] = score_data['score']
    #         item['confidence'] = score_data['confidence']

    #         return item

    #     return list(map(lambda x: set_score(x), comments))

    def upload_feelings(self, comments):
        data = ""
        for item in comments:
            line = '&'.join([str(item['id']), str(item['feeling']),
                            str(item['score']), str(item['confidence'])]) + "#"
            if len(line.split('&')) == 4:
                data += line

        print(data)

        req = ERApi(method="patchscores",
                    entity=f"review/update", env=self.env)
        req.set_body({'data_content': data})
        res = req.execute()
        print(res.status_code)

    def update_feelings(self):
        # 1- Récupérer la liste des commentaires non calculés par 50
        # 2- calculer les feelings ... de ces commentaires
        # 3- upload les nouvelles valeurs
        # 4- Revenir à 1 tant que liste != liste vide

        page = 1
        while True:
            try:
                comments = self.get_comments(page)

                if len(comments) == 0:
                    break

                # new_comments = self.compute_scores(comments)
                # # print(new_comments)
                # self.upload_feelings(new_comments)
                page += 1

            except Exception as e:
                print(e)
                break

    def set_last_date(self, date):
        self.last_date = date

    def start(self):
        # refresh_connection()

        # counter = 0
        print("Liste des urls à sraper:")
        print(
            list(map(lambda x: {'url': x['url'], 'settings': x['id']}, self.settings.items)))

        for item in self.settings.items:
            time.sleep(random.randint(1, 3))

            print(
                f"****** {item['establishment_name']} / {item['source']} ******")

            if item['source'] in __class_name_v2__.keys():
                print("=> A scraper !!!")
                try:
                    instance = __class_name_v2__[item['source']](
                        url=item['url'], establishment=item['establishment_id'], settings=item['id'], env=self.env)

                    print('=> ', item['id'], ': ', item['url'])

                    if item['last_review_date']:
                        if self.last_date:
                            if datetime.strptime(self.last_date, "%d/%m/%Y") < datetime.strptime(item['last_review_date'], "%d/%m/%Y"):
                                instance.set_last_date(
                                    item['last_review_date'])
                            else:
                                instance.set_last_date(self.last_date)
                        else:
                            instance.set_last_date(item['last_review_date'])

                    instance.execute()
                except Exception as e:
                    print(e)
                    pass

                # if counter == 4:
                #     counter == 0
                #     refresh_connection()

            else:
                print(
                    f"!!!!!!!!! {item['source']} n'as dans la liste !!!!!!!!!!")
