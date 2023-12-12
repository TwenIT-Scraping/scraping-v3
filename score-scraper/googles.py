from scraping import Scraping
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


class Google(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        defurl = url if url.endswith('.fr.html') else f"{url}.fr.html"
        super().__init__(in_background=False, url=defurl,
                         establishment=establishment, env=env)

        self.attr = 'class'
        self.balise = 'div'
        self.css_selector = 'FBsWCd'


# trp = Google(url="https://www.google.com/travel/hotels/entity/ChYIqtL21OvSv65QGgovbS8wdnB3cTRzEAE/reviews?utm_campaign=sharing&utm_medium=link&utm_source=htls&ts=CAESABogCgIaABIaEhQKBwjnDxAKGAISBwjnDxAKGAMYATICEAAqCQoFOgNNR0EaAA", establishment=3, env="DEv")
# trp.execute()
# print(trp.data)
