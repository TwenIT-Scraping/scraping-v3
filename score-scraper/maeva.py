from scraping import Scraping
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup


class Maeva(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        defurl = url if url.endswith('.html') else f"{url}.fr.html"
        super().__init__(in_background=True, url=defurl,
                         establishment=establishment, env=env)

        self.attr = 'class'
        self.balise = 'span'
        self.css_selector = 'avis-verifies-note bold'
        self.source = 'maeva'

    def extract(self) -> None:
        try:
            self.driver.find_element(
                By.ID, "#fiche-produit-avis__container").click()
        except:
            pass

        time.sleep(2)

        page = self.driver.page_source
        soupe = BeautifulSoup(page, 'lxml')

        score = float(soupe.find(self.balise, {self.attr: self.css_selector}).text.strip(
        ).replace(',', '.').split('/')[0]) if soupe.find(self.balise, {self.attr: self.css_selector}) else 0

        self.data = score


# trp = Maeva(url="https://www.maeva.com/fr-fr/residence-cannes-villa-francia---maeva-home_49993.html",
#             establishment=4, env="DEV")
# trp.execute()
# print(trp.data)
