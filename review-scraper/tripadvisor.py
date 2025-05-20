import sys
from botasaurus.browser import browser, Driver, Wait
from botasaurus.profiles import Profiles
from botasaurus.user_agent import UserAgent
from botasaurus.soupify import soupify
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import time
import random
from changeip import refresh_connection
import json
import os
import requests

API_TOKEN_PROD="Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MTc1MjEzNDAsImV4cCI6MzI3MjcyMTM0MCwicm9sZXMiOlsiUk9MRV9FUkVQIiwiUk9MRV9DVVNUT01FUiIsIlJPTEVfQVBJIiwiUk9MRV9VU0VSIl0sInVzZXJuYW1lIjoic2NyYXBAbmV4dGllcy5sYW4ifQ.SOZZSGN2srNGnR79SIlYkxIoi6_4Ei-wLA6uh5tWmbkBDtnQX50uuLO2ZEX_yymEouvC97WQUzWo2-_ArBzXnkyHzHZnAtIbZ23FHN3UGkKoez_z6r6zS3iUQV66xywwiEnPUMGzHK8nfZIy5hLdYzFxG937U3nrQN7IJ2neLnzeIid8VIz-m9rulDkKRkDC_C8BEdg5E_N5KGlyZSb14KqTha0-3WTTBt6wFhQIKY70FsdWClCGB_WwSUaAT_aSCZNZxcbDa6z9IS7Tw_auwCuyJfj8_Pztpy9eHswE_Nw3niHJJQz5yZBZoonpHS7poIPxZCzbF1qGFAmAG_jk4A"
API_ENDPOINT = "https://api.nexties.fr/api/review/multi"



DATA_SOURCE = [
    # {'id': 297, 'caption': '', 'section': 'REVIEWS', 'establishment_name': 'Tamassa', 'establishment_id': 81, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Hotel_Review-g612353-d736372-Reviews-Tamassa_Resort-Bel_Ombre.html', 'language': 'en', 'last_review_date': None},
    {'id': 289, 'caption': '', 'section': 'REVIEWS', 'establishment_name': 'LUX Le Morne', 'establishment_id': 77, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Hotel_Review-g488105-d316737-Reviews-LUX_Le_Morne-Le_Morne.html', 'language': 'en', 'last_review_date': None},
    # {'id': 287, 'caption': '', 'section': 'REVIEWS', 'establishment_name': 'LUX Grand Baie', 'establishment_id': 75, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Hotel_Review-g488103-d302263-Reviews-LUX_Grand_Baie-Grand_Baie.html', 'language': 'en', 'last_review_date': None},
    # {'id': 268, 'caption': '', 'section': 'REVIEWS', 'establishment_name': 'LUX Saint Gilles', 'establishment_id': 79, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Hotel_Feature-g298470-d1473791-zft1-Lux_Saint_Gilles.html', 'language': 'en', 'last_review_date': '02/01/2024'},
    # {'id': 262, 'caption': '', 'section': 'REVIEWS', 'establishment_name': 'LUX Belle Mare', 'establishment_id': 76, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Hotel_Review-g298342-d316743-Reviews-Lux_Belle_Mare-Belle_Mare.html', 'language': 'en', 'last_review_date': '12/09/2024'},
    # {'id': 228, 'caption': '', 'section': 'REVIEWS', 'establishment_name': 'LUX Grand Gaube', 'establishment_id': 70, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Hotel_Review-g488104-d316747-Reviews-LUX_Grand_Gaube-Grand_Gaube.html', 'language': 'en', 'last_review_date': '04/09/2024'},
    # {'id': 179, 'caption': None, 'section': None, 'establishment_name': 'Chalet Iona', 'establishment_id': 53, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/VacationRentalReview-g580182-d8308071-Chalet_Iona_Meribel-Meribel_Les_Allues_Savoie_Auvergne_Rhone_Alpes.html', 'language': 'fr', 'last_review_date': '09/03/2018'},
    # {'id': 166, 'caption': None, 'section': 'REVIEWS', 'establishment_name': 'Les Rives marines', 'establishment_id': 50, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Hotel_Review-g1067666-d1068158-Reviews-Madame_Vacances_Residence_Les_Rives_Marines-Le_Teich_Gironde_Nouvelle_Aquitaine.html', 'language': 'fr', 'last_review_date': '04/09/2024'},
    # {'id': 144, 'caption': None, 'section': None, 'establishment_name': 'Hôtel du Golfe Ajaccio', 'establishment_id': 47, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Hotel_Review-g187140-d313054-Reviews-Hotel_du_Golfe-Ajaccio_Communaute_d_Agglomeration_du_Pays_Ajaccien_Corse_du_Sud_Corsica.html', 'language': 'fr', 'last_review_date': '12/09/2024'},
    # {'id': 137, 'caption': None, 'section': 'REVIEWS', 'establishment_name': 'Dolce Notte', 'establishment_id': 46, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Hotel_Review-g666541-d623991-Reviews-Hotel_Dolce_Notte-Saint_Florent_Haute_Corse_Corsica.html', 'language': 'fr', 'last_review_date': '03/09/2024'},
    # {'id': 104, 'caption': None, 'section': None, 'establishment_name': 'Restaurant Chacouette', 'establishment_id': 29, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Restaurant_Review-g1079358-d10302464-Reviews-Le_Central-Cap_Ferret_Lege_Cap_Ferret_Gironde_Nouvelle_Aquitaine.html', 'language': 'fr', 'last_review_date': '15/08/2023'},
    # {'id': 70, 'caption': None, 'section': None, 'establishment_name': 'Hotel Ibiza', 'establishment_id': 3, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Hotel_Review-g196707-d7120453-Reviews-Hotel_Ibiza-Les_Deux_Alpes_Isere_Auvergne_Rhone_Alpes.html', 'language': 'fr', 'last_review_date': '12/04/2024'},
    # {'id': 64, 'caption': None, 'section': None, 'establishment_name': 'ESF Chamonix', 'establishment_id': 23, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Attraction_Review-g187261-d2463830-Reviews-ESF_Chamonix_Ski_and_Guide_Company-Chamonix_Haute_Savoie_Auvergne_Rhone_Alpes.html', 'language': 'fr', 'last_review_date': '05/04/2024'},
    # {'id': 63, 'caption': None, 'section': None, 'establishment_name': 'La Fine Bouche', 'establishment_id': 22, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Restaurant_Review-g187261-d10491718-Reviews-La_Fine_Bouche-Chamonix_Haute_Savoie_Auvergne_Rhone_Alpes.html', 'language': 'fr', 'last_review_date': '17/08/2024'},
    # {'id': 62, 'caption': None, 'section': None, 'establishment_name': 'Le Comptoir des Alpes', 'establishment_id': 21, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Restaurant_Review-g187261-d13294436-Reviews-Le_Comptoir_des_Alpes-Chamonix_Haute_Savoie_Auvergne_Rhone_Alpes.html#photos;aggregationId=101&albumid=101&filter=7&ff=466724336', 'language': 'fr', 'last_review_date': '06/09/2024'},
    # {'id': 56, 'caption': None, 'section': None, 'establishment_name': 'Pierre & Vacances Residence La Rivière', 'establishment_id': 19, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Hotel_Review-g187261-d471965-Reviews-Pierre_Vacances_Residence_La_Riviere-Chamonix_Haute_Savoie_Auvergne_Rhone_Alpes.html#/media/471965/303132012:p/?albumid=101&type=0&category=101', 'language': 'fr', 'last_review_date': '27/08/2024'},
    # {'id': 55, 'caption': None, 'section': None, 'establishment_name': 'Grand Hôtel des Alpes', 'establishment_id': 18, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Hotel_Review-g187261-d558174-Reviews-Grand_Hotel_des_Alpes-Chamonix_Haute_Savoie_Auvergne_Rhone_Alpes.html', 'language': 'fr', 'last_review_date': '21/08/2024'},
    # {'id': 44, 'caption': None, 'section': None, 'establishment_name': 'Le Lido', 'establishment_id': 5, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Restaurant_Review-g1551846-d1555394-Reviews-Le_Lido-Tresserve_Savoie_Auvergne_Rhone_Alpes.html', 'language': 'fr', 'last_review_date': '27/08/2024'},
    # {'id': 38, 'caption': None, 'section': None, 'establishment_name': 'Office de Tourisme de Chamonix-Mont-Blanc', 'establishment_id': 12, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Attraction_Review-g187261-d12123950-Reviews-Office_de_Tourisme_de_Chamonix_Mont_blanc-Chamonix_Haute_Savoie_Auvergne_Rhone_A.html', 'language': 'fr', 'last_review_date': '21/02/2024'},
    # {'id': 14, 'caption': None, 'section': None, 'establishment_name': 'Les Chalets du Berger', 'establishment_id': 2, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Hotel_Review-g1056032-d1055274-Reviews-Madame_Vacances_Les_Chalets_de_Berger-La_Feclaz_Savoie_Auvergne_Rhone_Alpes.html', 'language': 'fr', 'last_review_date': '18/08/2024'},
    # {'id': 6, 'caption': None, 'section': None, 'establishment_name': 'Le Château de Candie', 'establishment_id': 4, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Hotel_Review-g8309764-d239781-Reviews-Chateau_de_Candie-Chambery_Savoie_Auvergne_Rhone_Alpes.html', 'language': 'fr', 'last_review_date': '11/08/2024'},
    # {'id': 1, 'caption': None, 'section': None, 'establishment_name': 'MV Transport', 'establishment_id': 8, 'idprovider': 1, 'category': 'Platform', 'source': 'Tripadvisor FR', 'url': 'https://www.tripadvisor.fr/Attraction_Review-g8309764-d15690584-Reviews-MV_Transport-Chambery_Savoie_Auvergne_Rhone_Alpes.html', 'language': 'fr', 'last_review_date': '01/03/2024'},
    # {'id': 82, 'caption': None, 'section': None, 'establishment_name': 'Hotel Chamartín The One', 'establishment_id': 28, 'idprovider': 23, 'category': 'Platform', 'source': 'Tripadvisor ES', 'url': 'https://www.tripadvisor.es/Hotel_Review-g187514-d228623-Reviews-Hotel_Chamartin_The_One-Madrid.html', 'language': 'es', 'last_review_date': '30/08/2024'},
    # {'id': 81, 'caption': None, 'section': 'REVIEWS', 'establishment_name': 'Hotel Antequera Hills', 'establishment_id': 27, 'idprovider': 23, 'category': 'Platform', 'source': 'Tripadvisor ES', 'url': 'https://www.tripadvisor.es/Hotel_Review-g315910-d325898-Reviews-Hotel_Antequera-Antequera_Costa_del_Sol_Province_of_Malaga_Andalucia.html', 'language': 'es', 'last_review_date': '03/09/2024'},
    # {'id': 296, 'caption': '', 'section': 'REVIEWS', 'establishment_name': 'Salt of Palmar', 'establishment_id': 80, 'idprovider': 18, 'category': 'Platform', 'source': 'Tripadvisor', 'url': 'https://www.tripadvisor.com/Hotel_Review-g1182872-d15125547-Reviews-Salt_Of_Palmar_Mauritius_A_Member_Of_Design_Hotels-Palmar.html', 'language': 'en', 'last_review_date': None},
    # {'id': 266, 'caption': '', 'section': 'REVIEWS', 'establishment_name': 'LUX South Ari Atoll', 'establishment_id': 78, 'idprovider': 18, 'category': 'Platform', 'source': 'Tripadvisor', 'url': 'https://www.tripadvisor.com/Hotel_Review-g6854954-d1053966-Reviews-LUX_South_Ari_Atoll-Dhidhoofinolhu_Island.html', 'language': 'en', 'last_review_date': '04/09/2024'},
    # {'id': 181, 'caption': None, 'section': 'REVIEWS', 'establishment_name': 'MV Transport', 'establishment_id': 8, 'idprovider': 18, 'category': 'Platform', 'source': 'Tripadvisor', 'url': 'https://www.tripadvisor.com/Attraction_Review-g8309764-d15690584-Reviews-MV_Transport-Chambery_Savoie_Auvergne_Rhone_Alpes.html', 'language': 'fr', 'last_review_date': '19/12/2023'},
    # {'id': 136, 'caption': None, 'section': 'REVIEWS', 'establishment_name': "Le Carre d'As", 'establishment_id': 44, 'idprovider': 18, 'category': 'Platform', 'source': 'Tripadvisor', 'url': 'https://www.tripadvisor.com/Restaurant_Review-g187259-d27427020-Reviews-Le_Carre_D_as-Aix_les_Bains_Savoie_Auvergne_Rhone_Alpes.html', 'language': 'fr', 'last_review_date': '31/08/2024'}
]

# Profiles.set_profile('amit', {'name': 'Amit Sharma', 'age': 30})
# Profiles.set_profile('rahul', {'name': 'Rahul Verma', 'age': 30})

# user_profiles = [
#     "Grand T",
#     "Philip",
#     "George",
#     "Greg"
# ]

# def get_profile(data):
#     return random.choice(data)

months_en_long = {
        'january': '01',
        'february': '02',
        'march': '03',
        'april': '04',
        'may': '05',
        'june': '06',
        'july': '07',
        'august': '08',
        'september': '09',
        'october': '10',
        'november': '11',
        'december': '12'
    }

months_en_short = {
    'jan': '01',
    'feb': '02',
    'mar': '03',
    'apr': '04',
    'may': '05',
    'jun': '06',
    'jul': '07',
    'aug': '08',
    'sep': '09',
    'oct': '10',
    'nov': '11',
    'dec': '12'
}

months_es_long = {
    'enero': '01',
    'febrero': '02',
    'marzo': '03',
    'abril': '04',
    'mayo': '05',
    'junio': '06',
    'julio': '07',
    'agosto': '08',
    'septiembre': '09',
    'octubre': '10',
    'noviembre': '11',
    'diciembre': '12'
}

months_es_short = {
    'ene': '01',
    'feb': '02',
    'mar': '03',
    'abr': '04',
    'may': '05',
    'jun': '06',
    'jul': '07',
    'ago': '08',
    'sep': '09',
    'oct': '10',
    'nov': '11',
    'dic': '12'
}

months_fr_long = {
    'janvier': '01',
    'février': '02',
    'mars': '03',
    'avril': '04',
    'mai': '05',
    'juin': '06',
    'juillet': '07',
    'août': '08',
    'septembre': '09',
    'octobre': '10',
    'novembre': '11',
    'décembre': '12'
}

months_fr_short = {
    'jan': '01',
    'fév': '02',
    'mar': '03',
    'avr': '04',
    'mai': '05',
    'jun': '06',
    'jui': '07',
    'aoû': '08',
    'sep': '09',
    'oct': '10',
    'nov': '11',
    'déc': '12'
}

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

def check_element_by_locator(element:object, locator:dict) -> bool:
    print(f"locator {locator}")
    element_found = False
    if locator['by_tag_only']:
        element_found = bool(element.find(locator['tag']))
    else:
        element_found = bool(element.find(locator['tag'], {locator['attr_key']:locator['attr_value']}))
    return element_found

def create_selector(locator:dict) -> str:
    return f"{locator['tag']}[{locator['attr_key']}='{locator['attr_value']}']"
    "{div[class='_T FKffI bmUTE']}"

def get_element_by_locator(element:object, locator:dict) -> object | None:
    if locator['by_tag_only']:
        element_found = element.find(locator['tag'])
        return element_found
    else:
        element_found = element.find(locator['tag'], {locator['attr_key']:locator['attr_value']})
        return element_found

def get_all_element_by_locator(element:object, locator:dict) -> object | None:
    if locator['by_tag_only']:
        element_found = element.find_all(locator['tag'])
        return element_found
    else:
        element_found = element.find_all(locator['tag'], {locator['attr_key']:locator['attr_value']})
        return element_found

def extract_element_by_locator(element:object, locator:dict) -> object | None:
    def clean_text(source:str) -> str:
        try:
            text = source.replace('\xa0', ' ').replace('\u00e9', 'é').replace('\u00a0', '').replace('\u00f3','ó').replace('\u2022', '').strip()
        except:
            pass
        return text
    if locator['by_tag_only']:
        element = element.find(locator['tag'])
    else:
        element = element.find(locator['tag'], {locator['attr_key']:locator['attr_value']})
    if element:
        match locator['target']:
            case "text":
                return clean_text(element.get_text())
            case "attribute":
                return clean_text(element[locator['value_attr']])
            case "child":
                sub_element = ''
                if locator['child']['by_tag_only']:
                    sub_element = element.find(locator['child']['tag'])
                else:
                    sub_element = element.find(locator['child']['tag'], {locator['child']['attr_key']:locator['child']['attr_value']})
                if locator['child']['target'] == 'attribute':
                    return clean_text(sub_element[locator['child']['value_attr']])
                else:
                    return clean_text(sub_element.get_text().strip())

    else:
        print('element not found')
        return

class TripadvisorPageDataExtractor(object):
    def __init__(self, page_data_source:dict, selectors:dict, settings:int, language:str, establishment:str) -> list | None:
        self.page_data_source = page_data_source
        self.selectors = selectors
        self.settings = settings
        self.language = language
        self.establishment = establishment

        self.page_data = []
        self.cleaned_data = []
        self.lang = ''
        self.page_type = get_page_type('tripadvisor', self.page_data_source['url'])
        self.source = 'tripadvisor'
        self.novisitday = '1'

        self.get_lang()
        self.extract()
        self.save()


    def extract(self) -> None:
        reviews = get_all_element_by_locator(self.page_data_source['web_page'], self.selectors['reviews'])
        print(f"==> {len(reviews)} cards found")
        if reviews:
            for item in reviews:
                review = {}
                for key in list(self.selectors['review'].keys()):
                    review[key] = extract_element_by_locator(item, self.selectors['review'][key])
                valid_data = True

                for key in list(review.keys()):
                    if review[key] is None:
                        if key == 'url':
                            continue
                        else:
                            valid_data = False
                            print(review)

                if valid_data:
                    self.page_data.append(review)

        # self.cleaned_data += self.page_data
        self.normalize_data()

        with open(f'./output/data_{self.establishment}.json',encoding='utf-8', mode='a') as openfile:
            openfile.write(json.dumps(self.cleaned_data, indent=4))

    def get_last_date(self) -> datetime:
        return datetime.strptime(self.cleaned_data[-1]['date_review'], '%d/%m/%Y')

    def get_lang(self) -> None:
        self.lang = urlparse(self.page_data_source['url']).netloc.split('.')[-1].lower()

    def format_date_hotel(self, date_str:str) -> object:
        today = datetime.now()
        match self.lang:
            case 'com':
                if 'yesterday' in date_str:
                    return (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')
                #format date for new type view hotel page 07 01 2025
                elif 'ago' in date_str:
                    date_split = date_str.replace('ago ','').strip().split(' ')
                    if date_split[0] == "1":
                        if date_split[1] == "day":
                            # input(f"{datetime.strftime(today + timedelta(days=-1), '%d/%m/%Y')}")
                            return datetime.strftime(today + timedelta(days=-1), '%d/%m/%Y')
                        if date_split[1] == "week":
                            # input(f"{datetime.strftime(today + timedelta(days=-7), '%d/%m/%Y')}")
                            return datetime.strftime(today + timedelta(days=-7), '%d/%m/%Y')
                        if date_split[1] == "month":
                            # input(f"{datetime.strftime(today + timedelta(days=-31), '%d/%m/%Y')}")
                            return datetime.strftime(today + timedelta(days=-31), '%d/%m/%Y')
                    else:
                        if date_split[1] == "days":
                            # input(f"{datetime.strftime(today + timedelta(days=-(int(date_split[0]))), '%d/%m/%Y')}")
                            return datetime.strftime(today + timedelta(days=-(int(date_split[0]))), '%d/%m/%Y')
                        if date_split[1] == "weeks":
                            # input(f"{datetime.strftime(today + timedelta(days=-7*(int(date_split[0]))), '%d/%m/%Y')}")
                            return datetime.strftime(today + timedelta(days=-7*(int(date_split[0]))), '%d/%m/%Y')
                        if date_split[1] == "months":
                            # input(f"{datetime.strftime(today + timedelta(days=-31*(int(date_split[0]))), '%d/%m/%Y')}")
                            return datetime.strftime(today + timedelta(days=-31*(int(date_split[0]))), '%d/%m/%Y')
                    #format date for new type view hotel page 07 01 2025
                else:
                    # date_split = date_str.split(' ')
                    # day = datetime.now().day if int(date_split[-1]) > 31 else date_split[-1]
                    # month = months_en_short[date_split[0][:3]]
                    # year = datetime.now().year if int(date_split[-1]) < 31 else date_split[-1]
                    # return f"{day}/{month}/{year}"

                    #modification pour la forme March 14, 2025 (modif 25 03 2025)
                    date_split = date_str.replace(',','').split(' ')
                    if len(date_split) == 3:
                        #jamais fausse car utilise le title (date_review)
                        day = date_split[1]
                        month = months_en_long[date_split[0].lower()]
                        year = date_split[2]
                        return f"{day}/{month}/{year}"
                    else:
                        # day = datetime.now().day if int(date_split[-1]) > 31 else date_split[-1]
                        day = "1" if int(date_split[-1]) > 31 else date_split[-1]
                        month = months_en_short[date_split[0][:3]]
                        year = datetime.now().year if int(date_split[-1]) < 31 else date_split[-1]
                        return f"{day}/{month}/{year}"
            case 'uk':
                if 'yesterday' in date_str:
                    return (datetime.now() - timedelta(days=-1)).strftime('%d/%m/%Y')
                else:
                    date_split = date_str.split(' ')
                    day = datetime.now().day if int(date_split[-1]) > 31 else date_split[-1]
                    month = months_en_short[date_split[0][:3]]
                    year = datetime.now().year if int(date_split[-1]) < 31 else date_split[-1]
                    return f"{day}/{month}/{year}"
            # case 'fr':
            #     if 'hier' in date_str:
            #         return (datetime.now() - timedelta(days=-1)).strftime('%d/%m/%Y')
            #     else:
            #         date_split = date_str.replace('en', '').strip().split(' ')
            #         print(date_split)
            #         if len(date_split) == 3:
            #             day = date_split[0]
            #             month = months_fr_short[date_split[1][:3]] if 'juin' not in date_split[1] else months_fr_short['jun']
            #             year = date_split[2]
            #             return f"{day}/{month}/{year}"
            #         if len(date_split) == 2:
            #             day = ''
            #             month = ''
            #             year = ''
            #             if date_split[0].isdigit() and int(date_split[0]) < 32:
            #                 day = date_split[0]
            #             else:
            #                 day = datetime.now().day
            #                 year = date_split[0]
            #             if date_split[0].isalpha():
            #                 month = months_fr_short[date_split[0][:3]] if 'juin' not in date_split[0] else months_fr_short['jun']
            #             if date_split[1].isdigit() and int(date_split[1]) > 32:
            #                 year = date_split[1]
            #             else:
            #                 month = months_fr_short[date_split[1][:3]] if 'juin' not in date_split[0] else months_fr_short['jun']
            #                 if not year:
            #                     year = datetime.now().year
            #             return f"{day}/{month}/{year}"
            case 'fr':
                if 'hier' in date_str:
                    return (datetime.now() - timedelta(days=-1)).strftime('%d/%m/%Y')
                #format date for new type hotel page 17 12 2024
                elif 'il y a' in date_str:
                    # input("MISY il y a amle date")
                    date_split = date_str.replace('il y a ','').strip().split(' ')
                    if date_split[0] == "1":
                        if date_split[1] == "jour":
                            # input(f"{datetime.strftime(today + timedelta(days=-1), '%d/%m/%Y')}")
                            return datetime.strftime(today + timedelta(days=-1), '%d/%m/%Y')
                        if date_split[1] == "semaine":
                            # input(f"{datetime.strftime(today + timedelta(days=-7), '%d/%m/%Y')}")
                            return datetime.strftime(today + timedelta(days=-7), '%d/%m/%Y')
                        if date_split[1] == "mois":
                            # input(f"{datetime.strftime(today + timedelta(days=-31), '%d/%m/%Y')}")
                            return datetime.strftime(today + timedelta(days=-31), '%d/%m/%Y')
                    else:
                        if date_split[1] == "jours":
                            # input(f"{datetime.strftime(today + timedelta(days=-(int(date_split[0]))), '%d/%m/%Y')}")
                            return datetime.strftime(today + timedelta(days=-(int(date_split[0]))), '%d/%m/%Y')
                        if date_split[1] == "semaines":
                            # input(f"{datetime.strftime(today + timedelta(days=-7*(int(date_split[0]))), '%d/%m/%Y')}")
                            return datetime.strftime(today + timedelta(days=-7*(int(date_split[0]))), '%d/%m/%Y')
                        if date_split[1] == "mois":
                            # input(f"{datetime.strftime(today + timedelta(days=-31*(int(date_split[0]))), '%d/%m/%Y')}")
                            return datetime.strftime(today + timedelta(days=-31*(int(date_split[0]))), '%d/%m/%Y')
                #fin format date for new type hotel page 17 12 2024
                else:
                    date_split = date_str.replace('en', '').strip().split(' ')
                    print(date_split)
                    # if len(date_split) == 3:
                    #     day = date_split[0]
                    #     month = months_fr_short[date_split[1][:3]] if 'juin' not in date_split[1] else months_fr_short['jun']
                    #     year = date_split[2]
                    #     return f"{day}/{month}/{year}"
                    # if len(date_split) == 2:
                    #     day = ''
                    #     month = ''
                    #     year = ''
                    #     if date_split[0].isdigit() and int(date_split[0]) < 32:
                    #         day = date_split[0]
                    #     else:
                    #         day = datetime.now().day
                    #         year = date_split[0]
                    #     if date_split[0].isalpha():
                    #         month = months_fr_short[date_split[0][:3]] if 'juin' not in date_split[0] else months_fr_short['jun']
                    #     if date_split[1].isdigit() and int(date_split[1]) > 32:
                    #         year = date_split[1]
                    #     else:
                    #         month = months_fr_short[date_split[1][:3]] if 'juin' not in date_split[0] else months_fr_short['jun']
                    #         if not year:
                    #             year = datetime.now().year
                    #     return f"{day}/{month}/{year}"

                    #mise à jour 27 03 2025
                    if len(date_split) == 3:
                        #format date type -> day month year (attribut title)
                        if date_split[0].isdigit() and date_split[1].isalpha() and date_split[2].isdigit():
                            day = date_split[0]
                            month = months_fr_long[date_split[1]]
                            year = date_split[2]
                            # input(f" DATE VAOVAO => {day}/{month}/{year}")
                            return f"{day}/{month}/{year}"
                        else:
                            day = date_split[0]
                            month = months_fr_short[date_split[1][:3]] if 'juin' not in date_split[1] else months_fr_short['jun']
                            year = date_split[2]
                            return f"{day}/{month}/{year}"
                    if len(date_split) == 2:
                        day = ''
                        month = ''
                        year = ''
                        if date_split[0].isdigit() and int(date_split[0]) < 32 and date_split[1].isalpha():
                            print('type de date = jour/mois')
                            day = date_split[0]
                            month = months_fr_short[date_split[1][:3]]
                            #pas de year donc on prend l'année en cours
                            year = datetime.now().year
                        
                        if date_split[0].isalpha() and date_split[1].isdigit() and int(date_split[1]) > 32:
                            print('type de date = mois/annee')
                            #pas de day, on prend le 1er car si jamais la date visite dépasse la date de review si la review a un day, c'est pas normal
                            day = "1"
                            month = months_fr_short[date_split[0][:3]]
                            year = date_split[1]
                        return f"{day}/{month}/{year}"
            case 'es':
                if 'ayer' in date_str:
                    return (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')
                else:
                    date_split = date_str.split(' ')
                    print(date_split)
                    if len(date_split) == 3:
                        day = date_split[0]
                        month = months_es_short[date_split[1][:3]]
                        year = date_split[2]
                        return f"{day}/{month}/{year}"
                    if len(date_split) == 2:
                        # date_split = date_str.split(' ')
                        # day = datetime.now().day if int(date_split[-1]) > 31 else date_split[-1]
                        #mise à jour 27 03 2025
                        day = "1" if int(date_split[-1]) > 31 else date_split[-1]
                        month = months_es_short[date_split[0][:3]]
                        year = datetime.now().year if int(date_split[-1]) < 31 else date_split[-1]
                        return f"{day}/{month}/{year}"

    def format_date_attraction(self, date_str:str) -> object:
        print(date_str)
        match self.lang:
            case 'com':
                if 'yesterday' in date_str:
                    return (datetime.now() - timedelta(days=-1)).strftime('%d/%m/%Y')
                else:
                    date_split = date_str.strip().split(' ')
                    if len(date_split) == 3:
                        day = date_split[1]
                        month = months_en_short[date_split[0][:3]]
                        year = date_split[2]
                        return f"{day}/{month}/{year}"
                    if len(date_split) == 2:
                        day = datetime.now().day
                        month = months_en_short[date_split[0][:3]]
                        year = date_split[1]
                        return f"{day}/{month}/{year}"
            case 'uk':
                if 'yesterday' in date_str:
                    return (datetime.now() - timedelta(days=-1)).strftime('%d/%m/%Y')
                else:
                    date_split = date_str.strip().split(' ')
                    if len(date_split) == 3:
                        day = date_split[1]
                        month = months_en_short[date_split[0][:3]]
                        year = date_split[2]
                        return f"{day}/{month}/{year}"
                    if len(date_split) == 2:
                        day = datetime.now().day
                        month = months_en_short[date_split[0][:3]]
                        year = date_split[1]
                        return f"{day}/{month}/{year}"
            case 'fr':
                #26 03 2025 , présence de "en famille, en couple sur les dates de visite, il y a déja cela dans les clean date mais je ne sais pas encore pourqoi c'est ici que ça marche"
                date_str = date_str.strip().replace(' en famille','').replace(' entre amis','').replace(' en couple','').strip()
                if 'hier' in date_str:
                    return (datetime.now() - timedelta(days=11)).strftime('%d/%m/%Y')
                else:
                    date_split = date_str.strip().split(' ')
                    print(date_split)
                    if len(date_split) == 3:
                        day = date_split[0]
                        month = months_fr_short[date_split[1][:3]] if 'juin' not in date_split[1] else months_fr_short['jun']
                        year = date_split[2]
                        return f"{day}/{month}/{year}"
                    if len(date_split) == 2:
                        day = datetime.now().day
                        month = months_fr_short[date_split[0][:3]] if 'juin' not in date_split[0] else months_fr_short['jun']
                        year = date_split[1]
                        return f"{day}/{month}/{year}"
            case 'es':
                if 'ayer' in date_str:
                    return (datetime.now() - timedelta(days=-1)).strftime('%d/%m/%Y')
                else:
                    date_split = date_str.strip().split(' ')
                    print(date_split)
                    if len(date_split) == 3:
                        day = date_split[0]
                        month = months_es_short[date_split[1][:3]]
                        year = date_split[2]
                        return f"{day}/{month}/{year}"
                    if len(date_split) == 2:
                        day = datetime.now().day
                        month = months_es_short[date_split[0][:3]]
                        year = date_split[1]
                        return f"{day}/{month}/{year}"

    def format_date_restaurant(self, date_str:str) -> object:
        print(date_str)
        match self.lang:
            case 'com':
                if 'yesterday' in date_str:
                    return (datetime.now() - timedelta(days=-1)).strftime('%d/%m/%Y')
                else:
                    date_split = date_str.strip().split(' ')
                    if len(date_split) == 3:
                        day = date_split[1]
                        month = months_en_short[date_split[0][:3]]
                        year = date_split[2]
                        return f"{day}/{month}/{year}"
                    if len(date_split) == 2:
                        day = datetime.now().day
                        month = months_en_short[date_split[0][:3]]
                        year = date_split[1]
                        return f"{day}/{month}/{year}"
            case 'uk':
                if 'yesterday' in date_str:
                    return (datetime.now() - timedelta(days=-1)).strftime('%d/%m/%Y')
                else:
                    date_split = date_str.strip().split(' ')
                    if len(date_split) == 3:
                        day = date_split[1]
                        month = months_en_short[date_split[0][:3]]
                        year = date_split[2]
                        return f"{day}/{month}/{year}"
                    if len(date_split) == 2:
                        day = datetime.now().day
                        month = months_en_short[date_split[0][:3]]
                        year = date_split[1]
                        return f"{day}/{month}/{year}"
            case 'fr':
                if 'hier' in date_str:
                    return (datetime.now() - timedelta(days=-1)).strftime('%d/%m/%Y')
                else:
                    date_split = date_str.strip().split(' ')
                    print(date_split)
                    if len(date_split) == 3:
                        day = date_split[0]
                        month = months_fr_short[date_split[1][:3]] if 'juin' not in date_split[1] else months_fr_short['jun']
                        year = date_split[2]
                        return f"{day}/{month}/{year}"
                    if len(date_split) == 2:
                        day = datetime.now().day
                        month = months_fr_short[date_split[0][:3]] if 'juin' not in date_split[0] else months_fr_short['jun']
                        year = date_split[1]
                        return f"{day}/{month}/{year}"
            case 'es':
                if 'ayer' in date_str:
                    return (datetime.now() - timedelta(days=-1)).strftime('%d/%m/%Y')
                else:
                    date_split = date_str.strip().split(' ')
                    print(date_split)
                    if len(date_split) == 3:
                        day = date_split[0]
                        month = months_es_short[date_split[1][:3]]
                        year = date_split[2]
                        return f"{day}/{month}/{year}"
                    if len(date_split) == 2:
                        day = datetime.now().day
                        month = months_es_short[date_split[0][:3]]
                        year = date_split[1]
                        return f"{day}/{month}/{year}"

    def format_date_vacation(self, date_str:str) -> object:
        print(date_str)
        match self.lang:
            case 'com':
                if 'yesterday' in date_str:
                    return (datetime.now() - timedelta(days=-1)).strftime('%d/%m/%Y')
                else:
                    date_split = date_str.strip().split(' ')
                    if len(date_split) == 3:
                        day = date_split[1]
                        month = months_en_short[date_split[0][:3]]
                        year = date_split[2]
                        return f"{day}/{month}/{year}"
                    if len(date_split) == 2:
                        day = datetime.now().day
                        month = months_en_short[date_split[0][:3]]
                        year = date_split[1]
                        return f"{day}/{month}/{year}"
            case 'uk':
                if 'yesterday' in date_str:
                    return (datetime.now() - timedelta(days=-1)).strftime('%d/%m/%Y')
                else:
                    date_split = date_str.strip().split(' ')
                    if len(date_split) == 3:
                        day = date_split[1]
                        month = months_en_short[date_split[0][:3]]
                        year = date_split[2]
                        return f"{day}/{month}/{year}"
                    if len(date_split) == 2:
                        day = datetime.now().day
                        month = months_en_short[date_split[0][:3]]
                        year = date_split[1]
                        return f"{day}/{month}/{year}"
            case 'fr':
                if 'hier' in date_str:
                    return (datetime.now() - timedelta(days=-1)).strftime('%d/%m/%Y')
                else:
                    date_split = date_str.strip().split(' ')
                    print(date_split)
                    if len(date_split) == 3:
                        day = date_split[0]
                        month = months_fr_short[date_split[1][:3]] if 'juin' not in date_split[1] else months_fr_short['jun']
                        year = date_split[2]
                        return f"{day}/{month}/{year}"
                    if len(date_split) == 2:
                        day = datetime.now().day
                        month = months_fr_short[date_split[0][:3]] if 'juin' not in date_split[0] else months_fr_short['jun']
                        year = date_split[1]
                        return f"{day}/{month}/{year}"
            case 'es':
                if 'ayer' in date_str:
                    return (datetime.now() - timedelta(days=-1)).strftime('%d/%m/%Y')
                else:
                    date_split = date_str.strip().split(' ')
                    print(date_split)
                    if len(date_split) == 3:
                        day = date_split[0]
                        month = months_es_short[date_split[1][:3]]
                        year = date_split[2]
                        return f"{day}/{month}/{year}"
                    if len(date_split) == 2:
                        day = datetime.now().day
                        month = months_es_short[date_split[0][:3]]
                        year = date_split[1]
                        return f"{day}/{month}/{year}"

    def format_date_hotel_feature(self, date_str:str) -> object:
        match self.lang:
            case 'com':
                if 'yesterday' in date_str:
                    return (datetime.now() - timedelta(days=-1)).strftime('%d/%m/%Y')
                else:
                    date_split = date_str.strip().split(' ')
                    if len(date_split) == 3:
                        day = date_split[1]
                        month = months_en_short[date_split[0][:3]]
                        year = date_split[2]
                        return f"{day}/{month}/{year}"
                    if len(date_split) == 2:
                        day = datetime.now().day
                        month = months_en_short[date_split[0][:3]]
                        year = date_split[1]
                        return f"{day}/{month}/{year}"
            case 'uk':
                if 'yesterday' in date_str:
                    return (datetime.now() - timedelta(days=-1)).strftime('%d/%m/%Y')
                else:
                    date_split = date_str.strip().split(' ')
                    if len(date_split) == 3:
                        day = date_split[1]
                        month = months_en_short[date_split[0][:3]]
                        year = date_split[2]
                        return f"{day}/{month}/{year}"
                    if len(date_split) == 2:
                        day = datetime.now().day
                        month = months_en_short[date_split[0][:3]]
                        year = date_split[1]
                        return f"{day}/{month}/{year}"
            case 'fr':
                if 'hier' in date_str:
                    return (datetime.now() - timedelta(days=-1)).strftime('%d/%m/%Y')
                else:
                    date_split = date_str.strip().split(' ')
                    #mise à jour 09 12 2024 ligne 588
                    date_split = date_str.replace('en', '').strip().split(' ')
                    print(date_split)
                    if len(date_split) == 3:
                        day = date_split[0]
                        month = months_fr_short[date_split[1][:3]] if 'juin' not in date_split[1] else months_fr_short['jun']
                        year = date_split[2]
                        return f"{day}/{month}/{year}"
                    if len(date_split) == 2:
                        day = datetime.now().day
                        month = months_fr_short[date_split[0][:3]] if 'juin' not in date_split[0] else months_fr_short['jun']
                        year = date_split[1]
                        return f"{day}/{month}/{year}"
            case 'es':
                if 'ayer' in date_str:
                    return (datetime.now() - timedelta(days=-1)).strftime('%d/%m/%Y')
                else:
                    date_split = date_str.strip().split(' ')
                    print(date_split)
                    if len(date_split) == 3:
                        day = date_split[0]
                        month = months_es_short[date_split[1][:3]]
                        year = date_split[2]
                        return f"{day}/{month}/{year}"
                    if len(date_split) == 2:
                        day = datetime.now().day
                        month = months_es_short[date_split[0][:3]]
                        year = date_split[1]
                        return f"{day}/{month}/{year}"

    def format_date(self, date_str:str) -> object:
        date_format_func = getattr(self, f"format_date_{self.page_type}")
        formated_date = date_format_func(date_str)
        print(formated_date)
        try:
            datetime.strptime(formated_date, "%d/%m/%Y")
            return formated_date
        except:
            print('failed to format date')

    def clean_author(self, author:str) -> object:
        if author and author != "":
            return author
        return None

    def clean_comment(self, comment:str) -> object:
        if comment and comment != "":
            comment.replace('$', 'USD').replace('\n', '').strip()
            return comment
        return None

    def clean_rating(self, rating:str) -> object:
        rating = rating.replace(',', '.')
        match(self.lang):
            case 'com':
                rating = rating.replace(' of ', '/').split(' ')[0]
                return rating
            case 'uk':
                rating = rating.replace(' of ', '/').split(' ')[0]
                return rating
            case 'fr':
                rating = rating.replace(' sur ', '/').split(' ')[0]
                return rating
            case 'es':
                rating = rating.replace(' de ', '/').split(' ')[0]
                return rating

    def clean_date_review(self, date:str) -> object:
        match self.page_type:
            case 'hotel':
                date = date.replace('(', '').replace(')', '').replace(',', '').replace('.', '').lower()
                match self.lang:
                    case 'com':
                        date = date.split('review ')[-1].strip()
                    case 'fr':
                        date = date.split('avis')[-1].strip()
                    case 'es':
                        if date.split(' ')[0].isdigit() and date.split(' ')[2].isalpha() and date.split(' ')[4].isdigit():
                            #nouvel affichage, mdification 25 03 2025
                            date = date.replace(' de ', ' ').strip()
                        else:
                            date = date.split('opinión')[-1].strip()
                            if date.split(' ')[0].isdigit():
                                date = ' '.join(date.split(' ')[::-1])
                    case 'uk':
                        date = date.split('review ')[-1].strip()
                        if date.split(' ')[0].isdigit():
                            date = ' '.join(date.split(' ')[::-1])
                return self.format_date(date)

            case 'hotel_feature':
                date = date.replace('(', '').replace(')', '').replace(',', '').lower()
                match self.lang:
                    case 'com':
                        date = date.split('review ')[-1].strip()
                    case 'fr':
                        date = date.split('avis')[-1].strip()
                    case 'es':
                        date = date.split('opinión')[-1].strip()
                        if date.split(' ')[0].isdigit():
                            date = ' '.join(date.split(' ')[::-1])
                    case 'uk':
                        date = date.split('review ')[-1].strip()
                        if date.split(' ')[0].isdigit():
                            date = ' '.join(date.split(' ')[::-1])
                return self.format_date(date)

            case 'attraction':
                date = date.replace('(', '').replace(')', '').replace(',', '').lower()
                match self.lang:
                    case 'com':
                        date = date.replace('written ', '')
                    case 'fr':
                        date = date.split(' le ')[-1]
                    case 'es':
                        date = date.split(' el ')[-1].replace(' de ', ' ')
                    case 'uk':
                        date = date.replace('written ', '')
                return self.format_date(date)

            case 'restaurant':
                date = date.replace('(', '').replace(')', '').replace(',', '').lower()
                match self.lang:
                    case 'com':
                        date = date.replace('written ', '')
                    case 'fr':
                        date = date.split(' le ')[-1]
                    case 'es':
                        date = date.split(' el ')[-1].replace(' de ', ' ')
                    case 'uk':
                        date = date.replace('written ', '')
                        #normalize date order
                        date_split = date.split(' ')
                        date = f"{date_split[1]} {date_split[0]} {date_split[2]}"
                return self.format_date(date)

            case 'vacation':
                date = date.split('.')[0].replace('(', '').replace(')', '').replace(',', '').lower()
                print(f"date review {date}")
                match self.lang:
                    case 'com':
                        date = date.replace('written ', '')
                    case 'fr':
                        date = date.split(' le ')[-1]
                    case 'es':
                        date = date.split(' el ')[-1].replace(' de ', ' ')
                    case 'uk':
                        date = date.replace('written ', '')
                        #normalize date order
                        date_split = date.split(' ')
                        date = f"{date_split[1]} {date_split[0]} {date_split[2]}"

                return self.format_date(date)

    def clean_date_visit(self, date:str) -> object:
        match self.page_type:
            case 'hotel':
                date = date.replace('(', '').replace(')', '').replace('.', '').lower()
                match self.lang:
                    case 'com':
                        date = date.split(': ')[-1].strip()
                    case 'fr':
                        date = date.split(': ')[-1].strip()
                    case 'es':
                        date = date.split(': ')[-1].strip().replace(' de ', ' ')
                    case 'uk':
                        date = date.split(': ')[-1].strip()
                return self.format_date(date)
            case 'hotel_feature':
                date = date.replace('(', '').replace(')', '').replace('.', '').lower()
                match self.lang:
                    case 'com':
                        date = date.split(': ')[-1].strip()
                    case 'fr':
                        date = date.split(': ')[-1].strip()
                    case 'es':
                        date = date.split(': ')[-1].strip().replace(' de ', ' ')
                    case 'uk':
                        date = date.split(': ')[-1].strip()
                return self.format_date(date)
            case 'attraction':
                date = date.replace('(', '').replace(')', '').replace('.', '').lower()
                match self.lang:
                    case 'com':
                        extra_words = ['couples', 'family', 'solo', 'friends', 'business']
                        for word in extra_words:
                            date = date.replace(word, '')
                    case 'fr':
                        extra_words = ['en couple', 'en famile', 'en solo', 'entre amis', 'entreprise']
                        for word in extra_words:
                            date = date.replace(word, '')
                        print(f"date before formating {date}")
                    case 'es':
                        extra_words = ['familia', 'parejas', 'en solitario', 'amigos', ' negocios', ' de']
                        for word in extra_words:
                            date = date.replace(word, '')
                    case 'uk':
                        extra_words = ['couples', 'family', 'solo', 'friends', 'business']
                        for word in extra_words:
                            date = date.replace(word, '')
                        date.strip()
                return self.format_date(date)
            case 'restaurant':
                date = date.replace('(', '').replace(')', '').replace('.', '').lower()
                match self.lang:
                    case 'com':
                        extra_words = ['couples', 'family', 'solo', 'friends', 'business']
                        for word in extra_words:
                            date = date.replace(word, '')
                        # print(f"date before formating {date}")
                    case 'fr':
                        # le double filtre est necessaire
                        extra_words = ['en couple', 'en famille', 'en solo', 'entre amis', 'entreprise']
                        for word in extra_words:
                            date = date.replace(word, '')
                        extra_words = ['couples', 'family', 'solo', 'friends', 'business']
                        for word in extra_words:
                            date = date.replace(word, '')
                        # print(f"date before formating {date}")
                    case 'es':
                        extra_words = ['familia', 'parejas', 'en solitario', 'amigos', ' negocios', ' de']
                        for word in extra_words:
                            date = date.replace(word, '')
                        extra_words = ['couples', 'family', 'solo', 'friends', 'business']
                        for word in extra_words:
                            date = date.replace(word, '')
                        # print(f"date before formating {date}")
                    case 'uk':
                        extra_words = ['couples', 'family', 'solo', 'friends', 'business']
                        for word in extra_words:
                            date = date.replace(word, '')
                        date.strip()
                        # print(f"date before formating {date}")
                return self.format_date(date)
            case 'vacation':
                date = date.split('.')[0].replace('(', '').replace(')', '').replace('.', '').lower()
                match self.lang:
                    case 'com':
                        date = date.split('visited ')[-1]
                        extra_words = [' traveled with family', 'couples', 'family', 'solo', 'friends', 'business']
                        for word in extra_words:
                            date = date.replace(word, '')
                        # print(f"date before formating {date}")
                    case 'fr':
                        # le double filtre es necessaire
                        date = date.split('visite ')[-1]
                        print(f'date visite {date}')
                        extra_words = ['en couple', 'en famille', 'en solo', 'entre amis', 'entreprise', 'a voyagé']
                        for word in extra_words:
                            date = date.replace(word, '')
                        extra_words = ['couples', 'family', 'solo', 'friends', 'business']
                        for word in extra_words:
                            date = date.replace(word, '')
                        print(f"date before formating {date}")
                    case 'es':
                        extra_words = ['familia', 'parejas', 'en solitario', 'amigos', ' negocios', ' de']
                        for word in extra_words:
                            date = date.replace(word, '')
                        extra_words = ['couples', 'family', 'solo', 'friends', 'business']
                        for word in extra_words:
                            date = date.replace(word, '')
                        # print(f"date before formating {date}")
                    case 'uk':
                        extra_words = ['couples', 'family', 'solo', 'friends', 'business']
                        for word in extra_words:
                            date = date.replace(word, '')
                        date.strip()
                        # print(f"date before formating {date}")
                return self.format_date(date)

    def clean_url(self, url:str=None) -> str:
        if not url:
            return self.page_data_source['url']
        return urlparse(self.page_data_source['url']).netloc + url

    def normalize_data(self) -> None:
        for data in self.page_data:
            new_data = {}
            for key in list(data.keys()):
                cleaner = getattr(self, f"clean_{key}")
                new_data[key] = cleaner(data[key])

            new_data['source'] = self.source
            new_data['language'] = self.language
            new_data['settings'] = self.settings
            new_data['novisitday'] = self.novisitday
            new_data['establishment'] = self.establishment

            #10 04 2025 , es établissements n'ont pas de langue depuis l'api, et ça bloque le sauvegarde, ajout langue selon site:
            if new_data['language'] == None:
                # print('language etablissement = None')
                # input(f'Self.lang (avant de mettre dans le new_data[language]) => {self.lang} ')
                if self.lang == "com":
                    self.lang = "en"
                    
                new_data['language'] = self.lang

            if 'https://' not in new_data['url']:
                new_data['url'] = 'https://' + new_data['url']

            print(new_data)
            self.cleaned_data.append(new_data)

    def post_data(self, cleaned_data:list) -> None:
        """## Post data to the API

        ### Args:
            - `cleaned_data (list)`: data to be sent
        """

        global API_ENDPOINT, API_TOKEN_PROD
        data = { "data_content": cleaned_data }
        encoded_data = json.dumps(data)
        try:
            response = requests.post(
                url= API_ENDPOINT,
                headers = {
                    'Authorization': API_TOKEN_PROD
                },
                data=encoded_data,
                verify=False,
                timeout=60)
            print(f"server response {response.status_code}")
            print(response.json())
        except Exception as e:
            print(e)

    def save(self) -> None:
        """## Post correct data to the API
        """
        print(" ==> saving ...")
        def split_data(data_to_split:list, by:int) -> list:
            """## split a large of list of data in to small list

            ### Args:
                - `data_to_split (list)`: list of big data to b
                - `by (int)`: number of peace of list

            ### Returns:
                - `list`: list contains splitted list of data
            """
            return [data_to_split[i:i + by] for i in range(0, len(data_to_split), by)]

        data_count = len(self.cleaned_data)
        print(f" {data_count} data to upload")
        self.post_data(self.cleaned_data)

def load_selectors(selector_name:str) -> dict:
    """## Load the selector from the json file

    ### Args:
        - `selector_name (str)`: the key name of the selector to be load

    ### Returns:
        - `dict`: the value of selector
    """

    with open(f"{os.path.abspath(__file__).replace('.py', '.json')}", 'r') as openfile:
        data = json.load(openfile)
        # print(data)
        try:
            return data[selector_name]
        except KeyError:
            return

def build_selectors(page:str, selectors:list) -> dict | None:
    """## generate a selector from multiple selectors saved

    ### Args:
        - `page (str)`: web page source code
        - `selectors (list)`: selectors which has multiple value

    ### Returns:
        - `dict | None`: dictionary contains correct selector for the page or None if not found or missing
    """

    new_selector = {
        "pagination_type": selectors['pagination_type'],
        "reviews": {},
        "review": {}
    }

    print("  ==> checking selectors")
    #check the correct container locator
    for container in selectors['container_locator']:
        if bool(get_element_by_locator(page, container)):
            new_selector['container_locator'] = container
            break

    container = get_element_by_locator(page, new_selector['container_locator'])

    #check the correct paginator locator
    for paginator in selectors['paginator_locator']:
        print('  ==> checking paginator')
        if bool(get_element_by_locator(container, paginator)):
            new_selector['paginator_locator'] = create_selector(paginator)
            break

    #check the reviews locator
    print(f"selectors reviews {selectors['reviews']}")
    for item in selectors['reviews']:
        if check_element_by_locator(page, item):
            new_selector['reviews'] = item
            break

    if bool(new_selector['reviews']):
        reviews = get_all_element_by_locator(container, new_selector['reviews'])
        #get first review in order to check key locator
        review = reviews[0]
        required_review_keys = [item for item in list(selectors['review'].keys()) if item not in selectors['optional_fields']]
        for key in required_review_keys:
            for item_locator in selectors['review'][key]:
                if get_element_by_locator(review, item_locator):
                    # assing the key of review with the correct selector
                    new_selector['review'][key] = item_locator
                    break

        #check missing key of review selector
        current_new_selector_keys = [item for item in list(new_selector['review'].keys()) if item not in selectors['optional_fields']]
        if set(required_review_keys) == set(current_new_selector_keys):
            print(' ==> valid selector generated')
            return new_selector
        else:
            print("  ==> selectors have missing keys")
            for key in required_review_keys:
                if key not in list(new_selector['review'].keys()) and key != 'url':
                    print(f"  => {key} correct selector not found")
                    print(new_selector)
                    return
    print(" ==> No reviews selector valid ")
    print(" ==> please check page and add it on selector file")
    input(" ==> press ctr + C and run again to retry or enter to by pass")

# def check_for_captcha(driver: Driver, locators:list) -> None:
#     print("  ==> checking for captcha")


@browser(user_agent=UserAgent.RANDOM,
         headless=False,
         add_arguments=[
                "---disable-translate",
                "--disable-geolocation",
                "--disable-gpu",
                "--disable-fingerprinting"])
def tripadvisor_task(driver: Driver, data:list):
    print(f"path : {os.path.abspath(__file__)}")
    try:
        refresh_connection()
    except:
        refresh_connection()
    driver.get(data['url'])
    driver.long_random_sleep()

    filtre_url_errone = ["https://www.tripadvisor.fr/Restaurant_Review-g187265-d2278761-Reviews-Le_Beranger-Lyon_Rhone_Auvergne_Rhone_Alpes.html", "https://www.tripadvisor.fr/sa=X&sca_esv=38d63245fe7a3678&tbm=lcl&sxsrf=ADLYWIL_b4jFRw12_uVmNs2c44K-Zi4wAQ:1730585967685&q=Les+Gourmands+Disent+Avis&rflfq=1&num=20&stick=H4sIAAAAAAAAAONgkxK2MDMzNzAyNzczNrA0MbcwMTQw2cDI-IpR0ie1WME9v7QoNzEvpVjBJbM4Na9EwbEss3gRK245AKsQJutSAAAA&rldimm=8667027763094784104&hl=fr-FR&ved=2ahUKEwj-su2O176JAxVEVqQEHQ2THcEQ9fQKegQIORAF&biw=1920&bih=927&dpr=1#lkt=LocalPoiReviews" ]

    if data['url'] not in filtre_url_errone:
        page_type = get_page_type('tripadvisor', driver.current_url)
        print(f"  ==> page type: {page_type}")
        if page_type == 'unknown':
            print("selector not define for this page")
            driver.prompt()
        else:
            selectors = load_selectors(page_type)
            reviews = []
            page = 0
            if selectors:
                print(f"\t ==> go to {driver.current_url}")
                driver.short_random_sleep()
                if selectors['has_pagination'] and selectors['pagination_type'] == 'button':
                    while True:
                        captcha_selectors = load_selectors('captcha')
                        # check page if captcha verification is found in the page
                        # check_for_captcha(driver, captcha_selectors)
                        for container_selector in selectors['container_locator']:
                            try:
                                driver.select(create_selector(container_selector)).scroll_into_view()
                            except:
                                pass
                        # check page if captcha verification is found in the page
                        # check_for_captcha(driver, captcha_selectors)

                        valid_selector = build_selectors(soupify(driver.page_html), selectors)
                        # comments = driver.select_all(create_selector(valid_selector['review']['comment']))
                        # for comment in comments:
                        #     comment.run_js(r"(el) => el.firstElementChild.style.max-height = none")

                        if valid_selector:
                            try:
                                page_data_source = {'web_page':soupify(driver.select(create_selector(valid_selector['container_locator']))), 'url': driver.current_url}
                                t = TripadvisorPageDataExtractor(
                                    page_data_source=page_data_source,
                                    selectors=valid_selector,
                                    settings=data['id'],
                                    establishment=data['establishment_id'],
                                    language=data['language'])
                                reviews += t.cleaned_data
                                container = driver.select(create_selector(valid_selector['container_locator']))
                                if 'paginator_locator' in list(valid_selector.keys()):
                                    next_page = container.select(valid_selector['paginator_locator'])
                                    if bool(next_page):
                                        next_page.scroll_into_view()
                                        # if t.get_last_date() < (datetime.now() - timedelta(days=365)):
                                        #     break
                                        #maj date condition 17 12 2024
                                        if (data['last_review_date'] == None) or (data['last_review_date'] == ""):
                                            if t.get_last_date() < (datetime.now() - timedelta(days=365)):
                                                print(f"{t.get_last_date()} < {(datetime.now() - timedelta(days=365))}")
                                                print("Last date valid reached")
                                                break
                                        else:
                                            if t.get_last_date() < datetime.strptime(data['last_review_date'], '%d/%m/%Y'):
                                                print(f"{t.get_last_date()} < {datetime.strptime(data['last_review_date'], '%d/%m/%Y')}")
                                                print("Last date valid reached")
                                                break
                                        time.sleep(.5)
                                        next_page.click()
                                        print(f"\t  ==> go to page {page + 2}")
                                        page += 1
                                        time.sleep(2)
                                        # check page if captcha verification is found in the page
                                        # check_for_captcha(soupify(driver.page_html), captcha_selecors)
                                else:
                                    print('pagination selector not found or not located')
                                    break
                            except Exception as e:
                                print(e)
                                break
                        else:
                            print("No valid selector found, please check page and add the selector.")
                            input(" press `ctrl + C` to stop or enter to by-pass this error")

                else:
                        pass
                    #     driver.select(selectors['container_locator']).scroll_into_view()
                    #     driver.sleep(random.randint(3,5))
                    #     page_data_source = {'web_page':soupify(driver.page_html), 'url': driver.current_url}
                    #     t = TripadvisorPageDataExtractor(
                    #         page_data_source=page_data_source,
                    #         selectors=selectors,
                    #         settings=data['id'],
                    #         establishment=data['establishment_id'],
                    #         language=data['language'])
                    #     reviews += t.cleaned_data
                    #     container = driver.select(valid_selector['container_locator'])
                    #     next_page = container.select(selectors['paginator_locator'])
                    #     if next_page:
                    #         next_page.scroll_into_view()
                    #         if t.get_last_date() < (datetime.now() - timedelta(days=365)):
                    #             break
                    #         next_page.click()
                    #         print(f"\t  ==> go to page {page + 2}")
                    #         page += 1
                    #     else:
                    #         print('pagination selector not found')
                    #         break

                print('scraping done')
                return {'reviews':reviews}
            else:
                print(f'selector not found for {driver.current_url}')
# if __name__ == "__main__":
#     tripadvisor_task(DATA_SOURCE)


# scrape_heading_task(data_url)




