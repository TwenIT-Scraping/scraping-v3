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


API_URL_PROD="https://api.nexties.fr/api/"
API_TOKEN_PROD="Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MTc1MjEzNDAsImV4cCI6MzI3MjcyMTM0MCwicm9sZXMiOlsiUk9MRV9FUkVQIiwiUk9MRV9DVVNUT01FUiIsIlJPTEVfQVBJIiwiUk9MRV9VU0VSIl0sInVzZXJuYW1lIjoic2NyYXBAbmV4dGllcy5sYW4ifQ.SOZZSGN2srNGnR79SIlYkxIoi6_4Ei-wLA6uh5tWmbkBDtnQX50uuLO2ZEX_yymEouvC97WQUzWo2-_ArBzXnkyHzHZnAtIbZ23FHN3UGkKoez_z6r6zS3iUQV66xywwiEnPUMGzHK8nfZIy5hLdYzFxG937U3nrQN7IJ2neLnzeIid8VIz-m9rulDkKRkDC_C8BEdg5E_N5KGlyZSb14KqTha0-3WTTBt6wFhQIKY70FsdWClCGB_WwSUaAT_aSCZNZxcbDa6z9IS7Tw_auwCuyJfj8_Pztpy9eHswE_Nw3niHJJQz5yZBZoonpHS7poIPxZCzbF1qGFAmAG_jk4A"


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
        case _: 
            return 'page'

        

class ScoreExtractor(object):

    def __init__(self, data:dict) -> dict:
        self.cleaned_data = {}
        self.settings = data.pop('settings')
        self.source = self.settings.get('source').lower().split(' ')[0]
        self.data = data
        self.score = 0.0
        self.env = self.data['env']

    def normalize_score(self) -> None:
        if 5 < self.score <= 10:
            self.score = self.score / 2

    def clean_score(self) -> None:
        try:
            self.score = float(self.score.strip().replace(',', '.'))
        except Exception as e:
            print(e)

    def get_clean_data(self) -> dict:
        self.clean_score()
        self.normalize_score()
        self.cleaned_data['score'] = self.score 
        self.cleaned_data['source'] = self.source
        self.cleaned_data['establishment'] = f"/api/establishments/{self.settings.get('establishment_id')}"
        self.cleaned_data['scoreDate'] = datetime.now().strftime("%Y-%m-%d")

        return self.cleaned_data

    def extract(self):
        score_source = bs4_ext.extract_element_by_locator(self.data.get('web_page'), self.data.get('selectors'))
        print(score_source)
        if score_source:
            self.score = score_source

    def post_data(self) -> None:
        """## Post data to the API

        ### Args:
            - `cleaned_data (list)`: data to be sent
        """
        print(f'posting {self.cleaned_data}')
        try:
            post_instance = ERApi(
                method="post", entity="scores", env=self.env, body=self.cleaned_data, params={})
            post_instance.execute()
        except Exception as e:
            print(e)

    def save(self):
        cleaned_data = self.get_clean_data()
        if cleaned_data:
            self.post_data()
        print('saving ...')
        with open('score.json', '+a') as openfile:
            openfile.write(json.dumps(str(self.cleaned_data)))


def build_selectors(page_element:str, selectors:dict) -> dict | None:
    print('building selectors')
    for selector_item in selectors:
        if bool(bs4_ext.extract_element_by_locator(page_element, selector_item)):
            return selector_item
    return None


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
        #  block_images_and_css=True,
        add_arguments=[
                "---disable-translate",
                "--disable-geolocation", 
                "--disable-gpu",
                "--disable-fingerprinting"])
def score_scraping_task(driver: Driver, data:list, env:str='PROD'):
    sites_with_captcha = [] #mettre dans cette liste les providers où il y a des captchas (différent en local et sur serveur)
    sites_needs_to_change_ip = ["thefork", "tripadvisor", "yelp"]
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
    provider = data['source'].lower().split(' ')[0]
    page_type = get_page_type(provider, driver.current_url)
    print(page_type)
    if provider == "google":
        print('Accept all cookies')
        try:
            button_accept_before_start_run_scrap = "#yDmH0d > c-wiz > div > div > div > div.NIoIEf > div.G4njw > div.AIC7ge > div.CxJub > div.VtwTSb > form:nth-child(2) > div > div > button"
            driver.click(button_accept_before_start_run_scrap, wait=Wait.SHORT)
            time.sleep(random.randint(1,2))
        except Exception as e:
            print(f'erreur => {e}')
    if page_type == 'unknown':
        print("selector not define for this page")
        driver.prompt()
    else:
        selectors = load_selectors(provider)[page_type]
        valid_selector = build_selectors(soupify(driver.page_html), selectors)
        print(valid_selector)
        score_container = driver.select(bs4_ext.create_selector(valid_selector))
        score_container.scroll_into_view()
        if valid_selector:
            s = ScoreExtractor(data={'selectors': valid_selector, 'settings': data,'env': env, 'web_page': soupify(driver.page_html)})
            s.extract()
            s.save()
        driver.close()

DATA_SOURCE = [
    # {'id': 296, 'caption': '', 'section': 'REVIEWS', 'external_url': None, 'establishment_name': 'Salt of Palmar', 'establishment_id': 80, 'establishment_tag': '66a1373b0298b', 'idprovider': 18, 'category': 'Platform', 'source': 'Tripadvisor', 'url': 'https://www.tripadvisor.com/Hotel_Review-g1182872-d15125547-Reviews-Salt_Of_Palmar_Mauritius_A_Member_Of_Design_Hotels-Palmar.html', 'language': 'en', 'last_review_date': '08/01/2021', 'last_comment_date': None, 'last_post_date': None},
    # {'id': 294, 'caption': '', 'section': '', 'external_url': None, 'establishment_name': 'LUX Saint Gilles', 'establishment_id': 79, 'establishment_tag': '66a0156222716', 'idprovider': 33, 'category': 'Platform', 'source': 'Booking', 'url': 'https://www.booking.com/reviews/re/hotel/lux-saint-gilles-resort.fr.html', 'language': 'en', 'last_review_date': '05/11/2024', 'last_comment_date': None, 'last_post_date': None},
    # {'id': 296, 'caption': '', 'section': 'REVIEWS', 'external_url': None, 'establishment_name': 'Salt of Palmar', 'enable': True, 'establishment_id': 80, 'establishment_tag': '66a1373b0298b', 'idprovider': 18, 'category': 'Platform', 'source': 'Tripadvisor', 'url': 'https://www.tripadvisor.com/Hotel_Review-g1182872-d15125547-Reviews-Salt_Of_Palmar_Mauritius_A_Member_Of_Design_Hotels-Palmar.html', 'language': 'en', 'last_review_date': '18/11/2024', 'last_comment_date': None, 'last_post_date': None},
    # {'id': 266, 'caption': '', 'section': 'REVIEWS', 'external_url': None, 'establishment_name': 'LUX South Ari Atoll', 'enable': True, 'establishment_id': 78, 'establishment_tag': '66a014696087d', 'idprovider': 18, 'category': 'Platform', 'source': 'Tripadvisor', 'url': 'https://www.tripadvisor.com/Hotel_Review-g6854954-d1053966-Reviews-LUX_South_Ari_Atoll-Dhidhoofinolhu_Island.html', 'language': 'en', 'last_review_date': '21/11/2024', 'last_comment_date': None, 'last_post_date': None},
    # {'id': 181, 'caption': None, 'section': 'REVIEWS', 'external_url': None, 'establishment_name': 'MV Transport', 'enable': True, 'establishment_id': 8, 'establishment_tag': '653f8ebb35238', 'idprovider': 18, 'category': 'Platform', 'source': 'Tripadvisor', 'url': 'https://www.tripadvisor.com/Attraction_Review-g8309764-d15690584-Reviews-MV_Transport-Chambery_Savoie_Auvergne_Rhone_Alpes.html', 'language': 'fr', 'last_review_date': '19/12/2023', 'last_comment_date': None, 'last_post_date': None},
    # {'id': 4, 'caption': None, 'section': None, 'establishment_name': "Résidence Les Balcons d'Aix - Vacancéole", 'establishment_id': 9, 'establishment_tag': '653fcf0dc46b5', 'idprovider': 6, 'category': 'Platform', 'source': 'Campings', 'url': 'https://www.campings.com/fr/camping/residence-les-balcons-d-aix-88189', 'last_review_date': '28/08/2023', 'language': 'fr'},
    # # {'id': 13, 'caption': None, 'section': None, 'external_url': None, 'establishment_name': 'Les Chalets du Berger', 'enable': True, 'establishment_id': 2, 'establishment_tag': '653f8cd1a2afd', 'idprovider': 9, 'category': 'Platform', 'source': 'Maeva', 'url': 'https://www.maeva.com/fr-fr/residence-les-chalets-du-berger-_695474.html', 'language': 'fr', 'last_review_date': '11/11/2024', 'last_comment_date': None, 'last_post_date': None},
    # {'id': 79, 'caption': None, 'section': None, 'external_url': None, 'establishment_name': 'Hotel Chamartín The One', 'enable': True, 'establishment_id': 28, 'establishment_tag': '65c36a97297d0', 'idprovider': 26, 'category': 'Platform', 'source': 'Booking ES', 'url': 'https://www.booking.com/reviews/es/hotel/chamartin.es.html?aid=356980&customer_type=total&order=completed_desc', 'language': 'es', 'last_review_date': '12/11/2024', 'last_comment_date': '13/11/2024', 'last_post_date': '02/11/2024'},
    # {'id': 293, 'caption': '', 'section': '', 'external_url': None, 'establishment_name': 'LUX Le Morne', 'enable': True, 'establishment_id': 77, 'establishment_tag': '66a013b44b921', 'idprovider': 34, 'category': 'Platform', 'source': 'Expedia', 'url': 'https://www.expedia.com/en/Le-Morne-Hotels-LUX-Le-Morne-Resort.h2245801.Hotel-Information', 'language': 'en', 'last_review_date': None, 'last_comment_date': None, 'last_post_date': None},
    # {'id': 84, 'caption': None, 'section': None, 'external_url': None, 'establishment_name': 'Hotel Chamartín The One', 'enable': True, 'establishment_id': 28, 'establishment_tag': '65c36a97297d0', 'idprovider': 24, 'category': 'Platform', 'source': 'Hotels.com ES', 'url': 'https://es.hotels.com/ho109553/hotel-chamartin-the-one-madrid-espana/?locale=es_US&pos=HCOM_US&siteid=300000001', 'language': 'es', 'last_review_date': '07/10/2024', 'last_comment_date': '13/11/2024', 'last_post_date': '02/11/2024'},
    # {'id': 12, 'caption': None, 'section': None, 'external_url': None, 'establishment_name': '28-50 Marylebone Lane', 'enable': True, 'establishment_id': 6, 'establishment_tag': '653f8d61dd3f9', 'idprovider': 7, 'category': 'Platform', 'source': 'Opentable UK', 'url': 'https://www.opentable.co.uk/28-50-marylebone', 'language': 'fr', 'last_review_date': '15/10/2024', 'last_comment_date': None, 'last_post_date': None},
    # {'id': 325, 'caption': '', 'section': '', 'external_url': None, 'establishment_name': 'La Cantine de Candie', 'enable': True, 'establishment_id': 99, 'establishment_tag': '672a4a29d9f52', 'idprovider': 21, 'category': 'Platform', 'source': 'Google', 'url': 'https://www.google.com/search?sa=X&sca_esv=e681ec4bfbfc45ae&tbm=lcl&sxsrf=ADLYWII9kVMtzIqwnI2Nm59hUiC17XALug:1730825416052&q=La+Cantine+de+Candie+Avis&rflfq=1&num=20&stick=H4sIAAAAAAAAAONgkxI2MTI0NDU0tzAxNDI2MDc2NTM02cDI-IpR0idRwTkxryQzL1UhJRXETMlMVXAsyyxexIpbDgAZvu5XUgAAAA&rldimm=4211517841230735614&hl=fr-FR&ved=2ahUKEwin792Q08WJAxVaQ6QEHYQRCxwQ9fQKegQINBAF&biw=1920&bih=927&dpr=1#lkt=LocalPoiReviews', 'language': 'fr', 'last_review_date': '17/11/2024', 'last_comment_date': None, 'last_post_date': None},
    # {'id': 271, 'caption': '', 'section': 'REVIEWS', 'external_url': None, 'establishment_name': 'Salt of Palmar', 'enable': True, 'establishment_id': 80, 'establishment_tag': '66a1373b0298b', 'idprovider': 2, 'category': 'Platform', 'source': 'Google Travel', 'url': 'https://www.google.com/travel/search?https://www.google.com/travel/search?gsas=1&ts=EggKAggDCgIIAxocEhoSFAoHCOgPEAkYCxIHCOgPEAkYDBgBMgIQAA&qs=MhNDZ29Jc0ttSHdZWEZzcFp1RUFFOAI&ap=ugEHcmV2aWV3cw&client=firefox-b-d&hl=fr-FR', 'language': 'en', 'last_review_date': '15/11/2024', 'last_comment_date': None, 'last_post_date': None},
    # {'id': 82, 'caption': None, 'section': None, 'external_url': None, 'establishment_name': 'Hotel Chamartín The One', 'enable': True, 'establishment_id': 28, 'establishment_tag': '65c36a97297d0', 'idprovider': 23, 'category': 'Platform', 'source': 'Tripadvisor ES', 'url': 'https://www.tripadvisor.es/Hotel_Review-g187514-d228623-Reviews-Hotel_Chamartin_The_One-Madrid.html', 'language': 'es', 'last_review_date': '10/11/2024', 'last_comment_date': '13/11/2024', 'last_post_date': '02/11/2024'},
    # {'id': 20, 'caption': None, 'section': None, 'external_url': None, 'establishment_name': '28-50 Marylebone Lane', 'enable': True, 'establishment_id': 6, 'establishment_tag': '653f8d61dd3f9', 'idprovider': 11, 'category': 'Platform', 'source': 'Yelp', 'url': 'https://www.yelp.com/biz/28-50-wine-workshop-and-kitchen-london', 'language': 'fr', 'last_review_date': None, 'last_comment_date': None, 'last_post_date': None},
    # {'id': 183, 'caption': None, 'section': 'REVIEWS', 'external_url': None, 'establishment_name': 'Sport2000 France', 'enable': True, 'establishment_id': 52, 'establishment_tag': '663df5f465c43', 'idprovider': 5, 'category': 'Platform', 'source': 'Trustpilot', 'url': 'https://fr.trustpilot.com/review/www.sport2000.fr', 'language': 'fr', 'last_review_date': '11/11/2024', 'last_comment_date': '25/06/2024', 'last_post_date': '30/08/2024'}
    # {'id': 31, 'caption': None, 'section': None, 'external_url': None, 'establishment_name': 'MV Transport', 'enable': True, 'establishment_id': 47, 'establishment_tag': '653681b7dea2f', 'idprovider': 5, 'category': 'Platform', 'source': 'Trustpilot', 'url': 'https://fr.trustpilot.com/review/www.mvtransport.fr', 'language': 'EN', 'last_review_date': '14/01/2022', 'last_comment_date': None, 'last_post_date': None}
#     {
#     "id": 7,
#     "caption": None,
#     "section": None,
#     "external_url": None,
#     "establishment_name": "Résidence Les Balcons d'Aix - Vacancéole",
#     "enable": True,
#     "establishment_id": 9,
#     "establishment_tag": "653fcf0dc46b5",
#     "idprovider": 2,
#     "category": "Platform",
#     "source": "Google Travel",
#     "url": "https://www.google.com/travel/search?gsas=1&ts=EggKAggDCgIIAxocEhoSFAoHCOgPEAYYGBIHCOgPEAYYGhgCMgIQAA&qs=MhRDZ3NJbzYtWnd1UE4xS3l5QVJBQjgC&ap=ugEHcmV2aWV3cw&hl=fr-FR&ved=0CAAQ5JsGahcKEwiYrNOJ2IyGAxUAAAAAHQAAAAAQBQ",
#     "language": None,
#     "last_review_date": None,
#     "last_comment_date": None,
#     "last_post_date": None
#   },
#   {
#     "id": 5,
#     "caption": None,
#     "section": None,
#     "external_url": None,
#     "establishment_name": "Résidence Les Balcons d'Aix - Vacancéole",
#     "enable": True,
#     "establishment_id": 9,
#     "establishment_tag": "653fcf0dc46b5",
#     "idprovider": 1,
#     "category": "Platform",
#     "source": "Tripadvisor FR",
#     "url": "https://www.tripadvisor.fr/Hotel_Review-g1067706-d1431734-Reviews-Vacanceole_Residence_Les_Balcons_d_Aix-Les_Deserts_Savoie_Auvergne_Rhone_Alpes.html",
#     "language": None,
#     "last_review_date": None,
#     "last_comment_date": None,
#     "last_post_date": None
#   },
#   {
#     "id": 4,
#     "caption": None,
#     "section": None,
#     "external_url": None,
#     "establishment_name": "Résidence Les Balcons d'Aix - Vacancéole",
#     "enable": True,
#     "establishment_id": 9,
#     "establishment_tag": "653fcf0dc46b5",
#     "idprovider": 6,
#     "category": "Platform",
#     "source": "Campings",
#     "url": "https://www.campings.com/fr/camping/residence-les-balcons-d-aix-88189",
#     "language": None,
#     "last_review_date": "28/08/2023",
#     "last_comment_date": None,
#     "last_post_date": None
#   }
]

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






