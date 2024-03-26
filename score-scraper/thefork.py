from scraping import Scraping
from changeip import refresh_connection
import time


class Thefork(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        refresh_connection()
        super().__init__(in_background=False, url=url,
                         establishment=establishment, env=env)

        self.attr = 'data-test'
        self.balise = 'span'
        self.css_selector = 'rating-value'
        self.source = 'thefork'

    def extract(self):

        input("Entrer une touche pour continuer ...")
        return super().extract()


# trp = Thefork(url="https://www.thefork.fr/restaurant/best-western-alexander-park-r308265/avis",
#               establishment=3, env="DEV")
# trp.execute()
# print(trp.data)
