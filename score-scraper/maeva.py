from scraping import Scraping
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


class Maeva(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        defurl = url if url.endswith('.html') else f"{url}.fr.html"
        super().__init__(in_background=False, url=defurl,
                         establishment=establishment, env=env)

        self.attr = 'class'
        self.balise = 'span'
        self.css_selector = 'score-text'


# trp = Maeva(url="https://www.maeva.com/fr-fr/residence-cannes-villa-francia---maeva-home_49993.html",
#             establishment=4, env="DEV")
# trp.execute()
# print(trp.data)
