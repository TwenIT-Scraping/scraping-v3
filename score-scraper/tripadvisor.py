from scraping import Scraping
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


class Tripadvisor(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, env=env)

        self.attr = 'data-automation'
        self.balise = 'div'
        self.css_selector = 'reviewBubbleScore'


trp = Tripadvisor(
    url="https://www.tripadvisor.fr/Attraction_Review-g3520917-d518281-Reviews-Courchevel-Saint_Bon_Tarentaise_Courchevel_Savoie_Auvergne_Rhone_Alpes.html", establishment=33, env="DEV")
trp.execute()
print(trp.data)
