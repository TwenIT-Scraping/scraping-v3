from scraping import Scraping
import time
from selenium.webdriver.common.by import By


class Hotels_FR(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        defurl = url if url.endswith('.fr.html') else f"{url}.fr.html"
        super().__init__(in_background=False, url=defurl,
                         establishment=establishment, env=env)
        self.source = 'hotels'

    def extract(self) -> None:
        time.sleep(2)

        score = float(self.driver.find_element(
            By.XPATH, "//meta[@itemprop='ratingValue']").get_attribute('content'))

        self.data = score / 2 if score > 5 else score


class Hotels_EN(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        defurl = url if url.endswith('.fr.html') else f"{url}.fr.html"
        super().__init__(in_background=False, url=defurl,
                         establishment=establishment, env=env)
        self.source = 'hotels'

    def extract(self) -> None:
        time.sleep(2)

        score = float(self.driver.find_element(
            By.XPATH, "//meta[@itemprop='ratingValue']").get_attribute('content'))

        self.data = score / 2 if score > 5 else score


# trp = Hotels(url="https://uk.hotels.com/ho512192/the-standard-high-line-new-york-united-states-of-america/",
#              establishment=33, env="dev")
# trp.execute()
# print(trp.data)
