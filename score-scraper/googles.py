from scraping import Scraping
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as ExC
from datetime import datetime


class Google(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        defurl = url if url.endswith('.fr.html') else f"{url}.fr.html"
        super().__init__(in_background=True, url=defurl,
                         establishment=establishment, env=env)


        if self.is_handball():
            self.attr = 'class'
            self.balise = 'span'
            self.css_selector = 'yi40Hd YrbPuc'
            self.source = 'google'
        else:    
            self.attr = 'class'
            self.balise = 'span'
            self.css_selector = 'fzTgPe Aq14fc'
            self.source = 'google'

       #pour cliquer ce qui bloque avant de scrapper sur serveur (c'était le problème principale) , 07 10 2024
    def extract(self) -> None:
        self.button_accept_before_start_run_scrap = "/html/body/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button/span"
        try:
            WebDriverWait(self.driver,10).until(ExC.element_to_be_clickable((By.XPATH, self.button_accept_before_start_run_scrap)))
            self.driver.find_element(By.XPATH, self.button_accept_before_start_run_scrap).click()
            print("Bouton accept cookie présent et cliqué")
            time.sleep(5)
        except:
            print("Pas de bouton accept cookie, donc go scrap")
            pass

        super().extract()
            

    def is_handball(self) -> bool:
        return True if '&topic=mid:/' in self.driver.current_url else False


class GoogleTravel(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        defurl = url if url.endswith('.fr.html') else f"{url}.fr.html"
        super().__init__(in_background=True, url=defurl,
                         establishment=establishment, env=env)

        self.attr = 'class'
        self.balise = 'div'
        self.css_selector = 'FBsWCd'
        self.source = 'google'
    
       #pour cliquer ce qui bloque avant de scrapper sur serveur (c'était le problème principale) , 07 10 2024
    def extract(self) -> None:
        self.button_accept_before_start_run_scrap = "/html/body/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button/span"
        try:
            WebDriverWait(self.driver,10).until(ExC.element_to_be_clickable((By.XPATH, self.button_accept_before_start_run_scrap)))
            self.driver.find_element(By.XPATH, self.button_accept_before_start_run_scrap).click()
            print("Bouton accept cookie présent et cliqué")
            time.sleep(5)
        except:
            print("Pas de bouton accept cookie, donc go scrap")
            pass

        super().extract()


# trp = Google(url="https://www.google.com/travel/hotels/entity/ChYIqtL21OvSv65QGgovbS8wdnB3cTRzEAE/reviews?utm_campaign=sharing&utm_medium=link&utm_source=htls&ts=CAESABogCgIaABIaEhQKBwjnDxAKGAISBwjnDxAKGAMYATICEAAqCQoFOgNNR0EaAA", establishment=3, env="DEv")
# trp.execute()
# print(trp.data)
