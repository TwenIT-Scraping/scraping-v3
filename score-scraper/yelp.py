from scraping import Scraping
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


class Yelp(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, env=env)

        self.attr = 'data-rating-typography'
        self.balise = 'p'
        self.css_selector = 'true'


trp = Yelp(url="https://www.yelp.com/biz/28-50-wine-workshop-and-kitchen-london",
           establishment=3, env="DEV")
trp.execute()
print(trp.data)
