from scraping import Scraping
import time
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup


class Tripadvisor(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, env=env, force_refresh=True)

        self.attr = 'data-automation'
        self.balise = 'div'
        self.css_selector = 'reviewBubbleScore'
        self.source = 'tripadvisor'


class Tripadvisor_UK(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, env=env, force_refresh=True)

        self.attr = 'data-automation'
        self.balise = 'div'
        self.css_selector = 'reviewBubbleScore'
        self.source = 'tripadvisor'


class Tripadvisor_FR(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, env=env, force_refresh=True)

        self.attr = 'class'
        self.balise = 'span'
        self.css_selector = 'uwJeR P'
        self.source = 'tripadvisor'

    def extract(self) -> None:
        time.sleep(5)

        if self.css_selector:
            while True:
                page = self.driver.page_source
                soupe = BeautifulSoup(page, 'lxml')

                with open('test.txt', 'w', encoding='utf-8') as f:
                    f.write(soupe.text.strip())

                print(len(soupe.find_all(self.balise, {
                    self.attr: self.css_selector})))

                score = float(soupe.find(self.balise, {self.attr: self.css_selector}).text.strip(
                ).replace(',', '.')) if soupe.find(self.balise, {self.attr: self.css_selector}) else 0

                self.data = score / 2 if score > 5 else score

                if score != 0:
                    break

                time.sleep(5)
                self.driver.refresh()

        if self.xpath_selector:
            score = float(self.driver.find_element(By.XPATH, self.xpath_selector).text) \
                if self.driver.find_element(By.XPATH, self.xpath_selector) else 0

            self.data = score / 2 if score > 5 else score


# trp = Tripadvisor(
#     url="https://www.tripadvisor.fr/Attraction_Review-g3520917-d518281-Reviews-Courchevel-Saint_Bon_Tarentaise_Courchevel_Savoie_Auvergne_Rhone_Alpes.html", establishment=33, env="DEV")
# trp.execute()
# print(trp.data)
