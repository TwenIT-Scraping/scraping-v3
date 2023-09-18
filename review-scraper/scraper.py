from models import Establishment
from booking import Booking
from maeva import Maeva
from campings import Campings
from hotels import Hotels
from googles import Google
from opentable import Opentable
from trustpilot import Trustpilot
from tripadvisor import Tripadvisor
from expedia import Expedia
from api import ERApi
import random
from changeip import refresh_connection
import time


__class_name__ = {
    'booking': Booking,
    'maeva': Maeva,
    'camping': Campings,
    'hotels': Hotels,
    'google': Google,
    'opentable': Opentable,
    'trustpilot': Trustpilot,
    'tripadvisor': Tripadvisor,
    'expedia': Expedia
}


class ListScraper:
    def __init__(self,):
        self.establishments = []
        self.ids = []
    
    def init(self, establishments=[]):
        etabs = ERApi.get_all('establishments')
        if len(establishments):
            self.ids = map(lambda y: y['id'], list(filter(lambda x: x['name'] in establishments, etabs)))
        else:
            self.ids = map(lambda x: x['id'], etabs)

        for item in self.ids:
            etab = Establishment(rid=item)
            etab.refresh()
            self.establishments.append(etab)

    def start(self, websites=[]):
        refresh_connection()

        for item in self.establishments:
            time.sleep(random.randint(1,5))
            
            print("****** Establishment: ", item.name, " ******")

            for site in item.websites.keys():
                if site in websites:
                    if site in __class_name__.keys():
                        print("===>\t", site)
                        instance = __class_name__[site](url=item.websites[site], establishment=item.id)
                        instance.execute()
                        print("\n\n")