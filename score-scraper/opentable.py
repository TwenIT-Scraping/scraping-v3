from scraping import Scraping
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


class Opentable(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, env=env)

        self.xpath_selector = "//div[@id='ratingInfo']/span"
        self.source = 'opentable'


class Opentable_UK(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, env=env)

        self.xpath_selector = "//div[@id='ratingInfo']/span"
        self.source = 'opentable'

# trp = Opentable("https://www.opentable.com/the-belvedere",
#                 establishment=4, env="DEV")
# trp.execute()
# print(trp.data)
