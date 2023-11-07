from models import Establishment, Settings
from booking import Booking
from maeva import Maeva
from campings import Campings
from hotels import Hotels_FR, Hotels_EN
from googles import Google
from opentable import Opentable, Opentable_UK
from trustpilot import Trustpilot
from tripadvisor import Tripadvisor_UK, Tripadvisor_FR
from expedia import Expedia
from api import ERApi
import random
from changeip import refresh_connection
import time


__class_name__ = {
    'booking': Booking,
    'maeva': Maeva,
    'camping': Campings,
    'hotels_com': Hotels_FR,
    'google': Google,
    'opentable': Opentable,
    'trustpilot': Trustpilot,
    'tripadvisor': Tripadvisor_UK,
    'expedia': Expedia
}

__class_name_v2__ = {
    'Booking': Booking,
    'Maeva': Maeva,
    'Campings': Campings,
    'Hotels.com FR': Hotels_FR,
    'Google': Google,
    'Google hotel': Google,
    'Opentable UK': Opentable_UK,
    'Trustpilot': Trustpilot,
    'Tripadvisor FR': Tripadvisor_FR,
    'Tripadvisor UK': Tripadvisor_UK,
    'Expedia': Expedia
}


class ListScraper:
    def __init__(self,):
        self.establishments = []
        self.ids = []

    def init(self, establishments=[]):
        instance = ERApi(entity="establishment/name")
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
    def __init__(self):
        self.settings = None

    def init(self, eid=None, ename=None, categ=None, source=None):
        self.settings = Settings(categ, eid, source, ename)
        self.settings.prepare()

    def start(self):
        # refresh_connection()

        # counter = 0

        # print(self.settings.items)

        for item in self.settings.items:
            time.sleep(random.randint(1, 3))

            print(
                f"****** {item['establishment_name']} / {item['source']} ******")

            if item['source'] in __class_name_v2__.keys():
                print("=> A scraper !!!")
                try:
                    instance = __class_name_v2__[item['source']](
                        url=item['url'], establishment=item['establishment_id'])
                    instance.execute()
                except Exception as e:
                    print(e)

                # if counter == 4:
                #     counter == 0
                #     refresh_connection()

            else:
                print(
                    f"!!!!!!!!! {item['source']} n'as dans la liste !!!!!!!!!!")
