from scraping import Scraping
import time


class Campings(Scraping):
    def __init__(self, url: str, establishment: str, env: str):
        # defurl = url if url.endswith('.fr.html') else f"{url}.fr.html" j'ai commenté car ça retourne un autre lien si on utilise le .fr.html
        super().__init__(in_background=False, url=url,
                         establishment=establishment, env=env)

        self.attr = 'class'
        # self.balise = 'span' ce n'est plus la balise utilisé (02 10 2024)
        self.balise = 'div'
        self.css_selector = 'summary__value'
        self.source = 'campings'


# trp = Campings(
#     url="https://www.campings.com/fr/camping/le-pearl-camping-paradis-76750#reviews", establishment=4, env="DEV")
# trp.execute()
# print(trp.data)
