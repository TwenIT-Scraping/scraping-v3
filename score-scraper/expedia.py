from scraping import Scraping
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


class Expedia(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        defurl = url if url.endswith('.fr.html') else f"{url}.fr.html"
        super().__init__(in_background=False, url=defurl,
                         establishment=establishment, env=env)

        self.xpath_selector = "//section[@id='Reviews']/div/div/div/div/div/div/span/div/div/div/span/div"
        self.source = 'expedia'


# trp = Expedia(url="https://www.expedia.com/Les-Deserts-Hotels-Vacanceole-Les-Balcons-DAix.h2481279.Hotel-Reviews",
#               establishment="4", env="DEV")
# trp.execute()
# print(trp.data)
