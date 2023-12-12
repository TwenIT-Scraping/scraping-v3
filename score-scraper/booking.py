from scraping import Scraping
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


class Booking(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        defurl = url if url.endswith('.fr.html') else f"{url}.fr.html"
        super().__init__(in_background=False, url=defurl,
                         establishment=establishment, env=env)
        self.attr = 'class'
        self.balise = 'span'
        self.css_selector = 'review-score-badge'


# trp = Booking(
#     url="https://www.booking.com/reviews/fr/hotel/la-belle-etoile-les-deux-alpes.fr.html", establishment="4", env='DEV')
# trp.execute()
# print(trp.data)
