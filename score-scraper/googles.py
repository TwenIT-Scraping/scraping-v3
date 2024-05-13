from scraping import Scraping
import time


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


# trp = Google(url="https://www.google.com/travel/hotels/entity/ChYIqtL21OvSv65QGgovbS8wdnB3cTRzEAE/reviews?utm_campaign=sharing&utm_medium=link&utm_source=htls&ts=CAESABogCgIaABIaEhQKBwjnDxAKGAISBwjnDxAKGAMYATICEAAqCQoFOgNNR0EaAA", establishment=3, env="DEv")
# trp.execute()
# print(trp.data)
