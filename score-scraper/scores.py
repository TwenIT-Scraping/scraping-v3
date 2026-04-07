import sys
from botasaurus.browser import browser, Driver, Wait
from botasaurus.profiles import Profiles
from botasaurus.user_agent import UserAgent
from botasaurus.soupify import soupify
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
from toolkits import bs4_extension as bs4_ext
from api import ERApi
from changeip import refresh_connection
import time 
import random
import json
import os


API_URL_PROD=os.getenv("API_URL_PROD")
API_TOKEN_PROD=os.getenv("API_TOKEN_PROD")


def get_page_type(origin:str,url:str) -> str:
    match(origin):
        case 'tripadvisor':
            url_source = url.split('-')[0]
            if "Restaurant_Review" in url_source:
                return 'restaurant'
            elif "Hotel_Review" in url_source:
                return 'hotel'
            elif 'Hotel_Feature' in url_source:
                return 'hotel_feature'
            elif "Attraction_Review" in url_source:
                return 'attraction'
            elif "VacationRentalReview" in url_source:
                return 'vacation'
            return 'unknown'
        case 'booking':
            if "/hotel/" in url:
                return 'hotel'
        case 'campings':
            if "camping/residence" in url:
                return 'residence'
        case 'maeva':
            if "/residence" in url:
                return 'residence'
        # case 'expedia':
        #     if "Hotel-Information" in url:
        #         return 'hotel'
        # case "hotels.com":
        #     if "/hotel" in url:
        #         return 'hotel'
        case "opentable":
            return "restaurant"
        case "google":
            # if "/search?sa" in url:
            #     return 'search'
            if "/travel" in url:
                return 'travel'
            else: #car si ce n'est pas travel vaut mieux tout de suite retourné le selecteur search
                return 'search'
        case "thefork":
            return "page"
        case _: 
            return 'page'

        

class ScoreExtractor(object):

    def __init__(self, data:dict) -> dict:
        self.cleaned_data = {}
        self.settings = data.pop('settings')
        self.source = self.settings.get('source').lower().split(' ')[0]
        self.data = data
        self.score = 0.0
        self.quantity = 0
        self.env = self.data['env']

    def normalize_score(self) -> None:
        if 5 < self.score <= 10:
            self.score = self.score / 2

    def clean_score(self) -> None:
        try:
            #ajput de replace '/' car sur serveur par exemple avec table de Lans l'affichage est différente du local
            self.score = float(self.score.strip().replace(',', '.').replace('/5',''))
        except Exception as e:
            print(e)

    def clean_quantity(self, site) -> int|None:
        #04 02 2026 , pour Google score, ajout de ce traitement car j'ai vu que le 'k' n'est pas pris en compte (exemple 11 k , donne 11 uniquement)
        if "https://www.google.com/search?" in site:
            # input(f"avant traitement quantity => {self.quantity} de GOOGLE NON TRAVEL")
            if 'k' in self.quantity.lower():
                print('k détecté dans le nombre de reviews')
                try:
                    digit_part = int(''.join(chiffre for chiffre in self.quantity if chiffre.isdigit()))
                    print(f'Avant clean > {self.quantity} | Après clean > {digit_part * 1000}')
                    self.quantity = digit_part * 1000
                except Exception as e:
                    input(f'Erreur dans le clean du quantity avec k -> {e}')
            else:
                #code qui était là avant, je l'ai mis ici
                try:
                    self.quantity = int(''.join(ch for ch in self.quantity if ch.isdigit()))
                    print(f'cleaned quantity: {self.quantity}')
                except Exception as e:
                    input(f'Erreur dans le clean du quantity -> {e}')

        else:
            #code qui était là avant, je l'ai mis ici
            try:
                self.quantity = int(''.join(ch for ch in self.quantity if ch.isdigit()))
                print(f'cleaned quantity: {self.quantity}')
            except Exception as e:
                input(f'Erreur dans le clean du quantity -> {e}')

    def clean_data(self, site) -> None:
        self.clean_score()
        self.clean_quantity(site) #04 02 2026 
        self.normalize_score()

    def get_clean_data(self, site) -> dict:
        self.clean_data(site)  #04 02 2026 parametre
        self.cleaned_data['score'] = self.score 
        self.cleaned_data['source'] = self.source
        self.cleaned_data['establishment'] = f"/api/establishments/{self.settings.get('establishment_id')}"
        self.cleaned_data['scoreDate'] = datetime.now().strftime("%Y-%m-%d")
        self.cleaned_data['quantity'] = self.quantity

        return self.cleaned_data

    def extract(self):
        score_source = bs4_ext.extract_element_by_locator(self.data.get('web_page'), self.data.get('selectors').get('scores'))
        # input(f'SCORE EXTRAIT => {score_source}')
        quantity_source = bs4_ext.extract_element_by_locator(self.data.get('web_page'), self.data.get('selectors').get('quantity'))
        # input(f'Quantity EXTRAIT => {quantity_source}')
        if score_source:
            self.score = score_source
        if quantity_source:
            self.quantity = quantity_source
        print(f'extracted score: {self.score} and quantity: {self.quantity}')

    def post_data(self) -> None:
        """## Post data to the API

        ### Args:
            - `cleaned_data (list)`: data to be sent
        """
        print('ON SAUVEGARDE')
        print(f'posting en cours ... {self.cleaned_data}')
        try:
            post_instance = ERApi(
                method="post", entity="scores", env=self.env, body=self.cleaned_data, params={})
            post_instance.execute()
        except Exception as e:
            input(f'Erreur de sauvegarde des scores --> {e}')

    def save(self, site):
        cleaned_data = self.get_clean_data(site)
        if cleaned_data:
            self.post_data()
            pass
        print('saving ...')
        with open('score.json', '+a') as openfile:
            openfile.write(json.dumps(str(self.cleaned_data)))

def build_selectors(page_element:str, selectors:dict) -> dict | None:
    print('building selectors ...')
    valide_selector = {}
    for items in selectors.keys():
        # print(f'checking selectors for {items} ...')
        for content in selectors.get(items):  
            # print(content)
            if bool(bs4_ext.get_element_by_locator(page_element, content)):
                valide_selector[items] = content
    
    if set(valide_selector.keys()) == set(selectors.keys()):
        return valide_selector
    else:
        for key in selectors.keys():
            if key not in valide_selector.keys():
                print(f'selector not found for {key}')
        return None
    
    # for selector_item in selectors:
    #     if bool(bs4_ext.extract_element_by_locator(page_element, selector_item)):
    #         return selector_item
    # return None


def load_selectors(selector_name:str) -> dict:
    """## Load the selector from the json file
    ### Args:
        - `selector_name (str)`: the key name of the selector to be load
    ### Returns:
        - `dict`: the value of selector
    """
    with open(f"{os.path.abspath(__file__).replace('.py', '.json')}", 'r') as openfile:
        data = json.load(openfile)
        try:
            return data[selector_name]
        except KeyError:
            return

@browser(user_agent=UserAgent.RANDOM,
         headless=False,
         block_images=True,
         block_images_and_css=True,
        add_arguments=[
                "---disable-translate",
                "--disable-geolocation", 
                "--disable-gpu",
                "--disable-fingerprinting"])
def score_scraping_task(driver: Driver, data:list, env:str='PROD'):
    sites_with_captcha = ["tripadvisor", "thefork"] #mettre dans cette liste les providers où il y a des captchas (différent en local et sur serveur)
    sites_needs_to_change_ip = ["thefork", "yelp"]
    if data['source'].lower().split(' ')[0] in sites_needs_to_change_ip:
        refresh_connection()
    try:
        try:
            driver.delete_cookies_and_local_storage()
        except:
            pass
        if urlparse(data['url']).netloc.split('.')[1] in sites_with_captcha:
            driver.get(data['url'], wait=Wait.SHORT)
            driver.prompt_to_solve_captcha()
        else:
            driver.get(data['url'], wait=Wait.SHORT)

    except TimeoutError:
        driver.reload()
    time.sleep(random.randint(2, 3))
    #Ce sont des urls n'ayant pas de score dans las page ou bien erroné (ça bloque les autres et j'ai mis comme ça)
    url_gourmand_false = "https://www.tripadvisor.fr/sa=X&sca_esv=38d63245fe7a3678&tbm=lcl&sxsrf=ADLYWIL_b4jFRw12_uVmNs2c44K-Zi4wAQ:1730585967685&q=Les+Gourmands+Disent+Avis&rflfq=1&num=20&stick=H4sIAAAAAAAAAONgkxK2MDMzNzAyNzczNrA0MbcwMTQw2cDI-IpR0ie1WME9v7QoNzEvpVjBJbM4Na9EwbEss3gRK245AKsQJutSAAAA&rldimm=8667027763094784104&hl=fr-FR&ved=2ahUKEwj-su2O176JAxVEVqQEHQ2THcEQ9fQKegQIORAF&biw=1920&bih=927&dpr=1#lkt=LocalPoiReviews"
    url_lux_saint_giles_errone = "https://www.tripadvisor.fr/Hotel_Feature-g298470-d1473791-zft1-Lux_Saint_Gilles.html"
    url_Restaurant_cafe_errone = "https://www.tripadvisor.fr/Restaurant_Review-g187265-d2278761-Reviews-Le_Beranger-Lyon_Rhone_Auvergne_Rhone_Alpes.html"
    url_google_travel_cafe_beranger = "https://www.google.com/travel/search?restaurant+café+comptoir+le+béranger+avis&sca_esv=581137776&sxsrf=AM9HkKkTxaU2EmD7HtSrp8Yn7nCXBlIrWA%3A1699604594342&ei=cuhNZYO_FJiKkdUP5eu3gAc&ved=0ahUKEwiDwOrAgLmCAxUYRaQEHeX1DXAQ4dUDCA8&uact=5&oq=restaurant+café+comptoir+le+béranger+avis&gs_lp=Egxnd3Mtd2l6LXNlcnAiK3Jlc3RhdXJhbnQgY2Fmw6kgY29tcHRvaXIgbGUgYsOpcmFuZ2VyIGF2aXMyBRAhGKABMgUQIRigAUi6C1DTAliyCnABeACQAQCYAXigAf8CqgEDNC4xuAEDyAEA-AEBwgIHECMYsAMYJ8ICBxAAGB4YsAPCAgQQIxgnwgIGEAAYFhgewgIFEAAYogTiAwQYASBBiAYBkAYC&sclient=gws-wiz-serp#ip=1"
    url_emulsion = "https://www.thefork.fr/restaurant/restaurant/l-emulsion-r692845"
    url_la_plage_google_non_travel = "https://www.google.com/search?sca_esv=582576413&sxsrf=AM9HkKmXy0A81vuU5L0jRo1vlbEvdIkcZw:1700043302352&uds=H4sIAAAAAAAA_-PS5mJxLMssFlIsSi0uSSwtSswrUchJVCjISUxPVUjMrFDISS1WSErMzCs2YBbi4mIQYpBiUGLQYAAACFT5zzkAAAA&si=ALGXSla_WCGdkD9yT_jdHrUlk6LMkmNSL3U2mfjKFmuVN40wv5RcbCQ1ZF6KDdkvkTmZQXh9aRdXSh28wTPTeKgCA76uxIHLkAoAN-9UGXnNHKqD3GsUwp0%3D&q=Restaurant+LA+PLAGE+Avis&sa=X&ved=2ahUKEwjgoI7p4sWCAxXHVaQEHT3mAhQQ3PALegQIRxAF&biw=1920&bih=927&dpr=1"
    url_errone = [url_gourmand_false, url_lux_saint_giles_errone, url_Restaurant_cafe_errone, url_google_travel_cafe_beranger, url_emulsion, url_la_plage_google_non_travel]
    #captcha for google non travel
    if "sorry" in driver.current_url:
        #for google not travel
        print("                 ")
        print("******************")
        print("remplis le captcha")
        print("******************")
        print("                 ")
        enteer = input("ENTER 'm' AFTER SOLVING CAPTCHA")
        while enteer.lower() != 'm':
            print("Captcha not solved, please solve it and enter 'm' to continue.")
            enteer = input("ENTER 'm' AFTER SOLVING CAPTCHA: ")
            if enteer.lower() == 'm':
                print("Captcha solved, continuing...")

    #03 04 2026 --sauter le nouvel affichage de booking non encore traité  pour ne pas pénaliser les autres booking qui fonctionnent bien
    if data['source'].lower().split(' ')[0] == "booking" and "https://www.booking.com/hotel" in driver.current_url: 
        print('nouvel affichage de booking, on saute cette url pour le moment en attendant de traiter le nouvel affichage')
        return

    #07 04 2026 : pour ne pas prendre en compte l'affichage en recherche simple de google
    if '/travel' not in driver.current_url:
        # input('GOOGLE NON TRAVEL')
        try:
            exist = driver.select('div[class="Q3DXx Efnghe"]') #c'est ce qui différencie une recherche normal sur la page google , d'une affichage normal pour un établissement
            if exist:
                print('page GOOGLE non recherche normal, on continue le scrap')
            else:
                print('PAGE DE RECHERCHE simple, pas de données scrapable, on saute l url pour le suivant')
                return
        except Exception as e:
            print('PAGE DE RECHERCHE simple, pas de données scrapable, on saute l url pour le suivant')
            return
    
    if data['url'] not in url_errone:    
        provider = data['source'].lower().split(' ')[0]
        page_type = get_page_type(provider, driver.current_url)
        print(page_type)
        if provider == "google":
            print('Accept all cookies')
            try:
                time.sleep(3)
                button_accept_before_start_run_scrap = "#yDmH0d > c-wiz > div > div > div > div.h22mC > div.jn2Duf > div.AIC7ge > div.CxJub > div.VtwTSb > form:nth-child(2) > div > div > button"
                # button_accept_before_start_run_scrap = "#yDmH0d > c-wiz > div > div > div > div.NIoIEf > div.G4njw > div.AIC7ge > div.CxJub > div.VtwTSb > form:nth-child(2) > div > div > button"
                driver.click(button_accept_before_start_run_scrap, wait=Wait.SHORT)
                time.sleep(random.randint(3,4))
            except Exception as error0:
                print(f'1er selecteur accept cookie not found => {error0}')
                try:
                    button_accept_before_start_run_scrap = "#yDmH0d > c-wiz > div > div > div > div.NIoIEf > div.jn2Duf > div.AIC7ge > div.CxJub > div.VtwTSb > form:nth-child(2) > div > div > button"

                    driver.click(button_accept_before_start_run_scrap, wait=Wait.SHORT)
                    time.sleep(random.randint(3,4))
                except Exception as error1:
                    print(f"2eme selecteur accept cookie not found => {error1}")
                    try:
                        button_accept_before_start_run_scrap = "#yDmH0d > c-wiz > div > div > div > div.NIoIEf > div.G4njw > div.AIC7ge > div.CxJub > div.VtwTSb > form:nth-child(2) > div > div > button"
                        driver.click(button_accept_before_start_run_scrap, wait=Wait.SHORT)
                        time.sleep(random.randint(3,4))
                    except Exception as e:
                        print(f"3eme selecteur accept cookie not found => {e}")
                        try:
                            button_accept_before_start_run_scrap = "#L2AGLb"
                            driver.click(button_accept_before_start_run_scrap, wait=Wait.SHORT)
                            time.sleep(random.randint(3,4))
                        except Exception as e:
                            print(f"4eme selecteur accept cookie not found => {e}")
                            input("manual click accept cookies, click ENTER to continue...")

                pass
        #ajout de temps pour google
        if provider == "google":
            driver.long_random_sleep()
            print("Pour google , rajoutant encore un peu d'attente")
            driver.short_random_sleep()

        if page_type == 'unknown':
            print("selector not define for this page")
            driver.prompt()
        else:
            selectors = load_selectors(provider)[page_type]
            valid_selector = build_selectors(soupify(driver.page_html), selectors)
            print(valid_selector)
            qt_container = driver.select(bs4_ext.create_selector(valid_selector.get('quantity')))
            qt_container.scroll_into_view()
            if valid_selector:
                s = ScoreExtractor(data={'selectors': valid_selector, 'settings': data,'env': env, 'web_page': soupify(driver.page_html)})
                s.extract()
                s.save(driver.current_url) #ajout parametre site 04 02 2026
            driver.close()
    #ajout temps d'attente avant reouverture driver
    driver.short_random_sleep()

# DATA_SOURCE = [
# {'id': 316, 'caption': None, 'settings_positioning': None, 'section': None, 'external_url': None, 'no_tracking': None, 'establishment_name': 'Comtes de Challes', 'enable': True, 'settings_language': None, 'establishment_id': 96, 'establishment_tag': '672653a091ee6', 'idprovider': 21, 'category': 'Platform', 'source': 'Google', 'url': 'https://www.google.com/search?sca_esv=6bf062aa074a1fec&hotel_occupancy=2&sxsrf=ADLYWIKfTFRuRn5_2G9mwiOT27RFd3hlTg:1730564878690&q=Comtes+de+Challes&uds=ADvngMgcma2krFDWAfXM9WWaYuEsJP7sYRLZXRKGNZH8JbiORDAsgngLv9VXY2Ieisztef0SoMY9tIO-TXBS04vCTHhhkCj7TBGxwC8EMKxDtkxlpmVGq-5KCPa14BOKbg4xCKQZTBdA&si=ACC90nwjPmqJHrCEt6ewASzksVFQDX8zco_7MgBaIawvaF4-7uLHuaLGrhRBJXK5sfBzKDSTRxOJ-Z0BjTGSZTfFBxFF-qlbnS-gwCOPSL9XvTBltVircXo%3D&sa=X&ved=2ahUKEwiRiOvGiL6JAxVvaqQEHa63Db4Q3PALegQIFxAE&biw=1920&bih=927&dpr=1', 'language': None, 'last_review_date': '20/10/2025', 'last_comment_date': None, 'last_post_date': None}
# ]

# providers = """Booking, Booking ES, 
#                 Booking FR, Booking MU, 
#                 Campings, Expedia, 
#                 Expedia ES, Expedia FR, 
#                 Google, Google Travel, 
#                 Hotels.com ES, Hotels.com FR, 
#                 Maeva, Opentable UK, Thefork, 
#                 Tripadvisor, Tripadvisor ES, 
#                 Tripadvisor FR, Trustpilot, Yelp"""

# if __name__ == '__main__':
#     score_scraping_task(DATA_SOURCE)






