from scraping import Scraping
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


class Trustpilot(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, env=env)

        self.attr = 'data-rating-typography'
        self.balise = 'p'
        self.css_selector = 'true'


trp = Trustpilot(url="https://fr.trustpilot.com/review/liberkeys.com",
                 establishment="4", env="DEV")
trp.execute()
print(trp.data)
