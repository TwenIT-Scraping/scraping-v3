from scraping import Scraping
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time


class Expedia(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        # defurl = url if url.endswith('.fr.html') else f"{url}.fr.html"
        # super().__init__(in_background=False, url=defurl,
        #                  establishment=establishment, env=env)
        super().__init__(in_background=False, url=url,
                         establishment=establishment, env=env)

        #nouveau selecteur Xpath 02 10 2024 (via firefox mais avec chrome ça n'a pas marché, le driver utilise firefox)
        self.xpath_selector = '/html/body/div[1]/div[1]/div/div[1]/div[2]/div[1]/div[3]/div/div/div[1]/div/div[2]/div/div[2]/span/span[1]'
        
        """ J'ai commenté le 02 10 2024 car on en a plus besoin , je ne sais pas pourquoi il y avait ça
        if self.url.endswith("Description-Hotel"):
            self.xpath_selector = "//meta[@itemprop='ratingValue']"

        if self.url.endswith("Avis-Voyageurs"):
            self.xpath_selector_2 = "//section[@id='Reviews']/div/div/div/div/div/div/span/div/div/div/span/div" """

        self.source = 'expedia'

    def extract(self) -> None:
        time.sleep(4) 
        """ commenté le 02 10 2024
        if self.xpath_selector:

            score = float(self.driver.find_element(By.XPATH, self.xpath_selector).get_attribute('content').replace(',', '.')) \
                if self.driver.find_element(By.XPATH, self.xpath_selector) else 0

        elif self.xpath_selector_2:
            score = float(self.driver.find_element(By.XPATH, self.xpath_selector_2).text.strip().replace(',', '.')) if self.driver.find_element(By.XPATH, self.xpath_selector_2) else 0"""
        if self.xpath_selector:
            score = float(self.driver.find_element(By.XPATH, self.xpath_selector).text.strip().replace(',','.')) if self.driver.find_element(By.XPATH, self.xpath_selector) else 0
        
        #j'ai ajouté la condition (02 10 2024) car il n'y en avait pas
        self.data = score / 2 if score > 5 else score 


# trp = Expedia(url="https://www.expedia.com/Les-Deserts-Hotels-Vacanceole-Les-Balcons-DAix.h2481279.Hotel-Reviews",
#               establishment="4", env="DEV")
# trp.execute()
# print(trp.data)
