from scraping import Scraping
import time


class Thefork(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, env=env)

        self.attr = 'data-test'
        self.balise = 'span'
        self.css_selector = 'rating-value'
        self.source = 'thefork'


# trp = Thefork(url="https://www.thefork.fr/restaurant/best-western-alexander-park-r308265/avis",
#               establishment=3, env="DEV")
# trp.execute()
# print(trp.data)
