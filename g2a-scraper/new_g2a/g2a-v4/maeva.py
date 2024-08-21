import argparse
from scraping import BaseScraping
from toolkits import constants
from toolkits.apis import G2A_API
from toolkits.validators import Maeva_Field_Validator
from toolkits.logger import report_bug, show_datatable

from colorama import Fore
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse
from datetime import datetime
import sys



class MaevaScraper(BaseScraping):

    def __init__(self, week_scrap: str, name: str, plateform: str, dest_name:str) -> None:
        super().__init__(week_scrap, name, plateform)
        self.dest_file_path = f"{constants.DESTS_FOLDER_PATH}/{plateform}/start/{'_'.join(self.week_scrap.split('/'))}/{dest_name}.json"
        self.url = ""
        self.stations = {}

    def load_station_list(self) -> None:
        print(Fore.GREEN + "\t ===> Initialisation liste stations ...")
        g2a_instance = G2A_API(entity="regions")
        page = 1

        while True:
            g2a_instance.set_page(page)
            results = g2a_instance.execute().json()

            if len(results) == 0:
                break

            for x in results:
                if x['website'] in ['/api/websites/1', '/api/websites/14']:
                    if x['name'] != '' and x['name'] not in self.stations.keys():
                        self.stations[x['name']] = x['region_key']

            page += 1
        print(f"\t ===> {len(self.stations)} stations loaded")

    def set_url(self, index:int) -> None:
        self.url = self.get_url(self.dest_file_path, index)

    def page_is_checked(self) -> bool:
        print("\t ===> checking page...")
        soupe = self.soupify_page()
        toast_indisponible = 0
        toaster_count = 0
        try:
            toasters = soupe.find('div', {'id':'fiche-seo-toaster-anchor'}).find_all('div', {'class':'toaster fiche-bloc-produit-item-b cursor-auto w100'})
            if toasters:
                toaster_count = len(toasters)
                for toast in toasters:
                    try:
                        toast.find('div', {'class':'toaster-right fiche_produit_indispo'})
                        toast_indisponible += 1
                    except:
                        pass

        except AttributeError:
            return False
        if soupe.find('div', {'data-info':'prix__container'}).find('div', {'class':'lazy-line-loader lllxl'}) and toast_indisponible == toaster_count:
            return False
        return True

    def clean_data(self) -> None:
        pass
        
    def extract_data(self) -> None:
        print("\t ===> extracting data ...")

        def remove_char(char:object):
            return str(char).replace(',', '-').replace('&', ' and ')

        def link_params(url):
            url_params = parse_qs(urlparse(url).query)
            sep = '/'
            try:
                n_offre = ''.join(url_params['id'][0].split('-')[::-1])
                start_date = sep.join(
                    url_params['date_debut'][0].split('-')[::-1])
                end_date = sep.join(url_params['date_fin'][0].split('-')[::-1])
                return n_offre, start_date, end_date
            except KeyError as e:
                print(e)
                return

        soupe = self.soupify_page()
        self.data_container = []

        if soupe.find('div', {'fiche-seo-toaster-container'}):
            toasters = soupe.find('div', {'id':'fiche-seo-toaster-anchor'}).find_all('div', {'class':'toaster fiche-bloc-produit-item-b cursor-auto w100'}) \
                if soupe.find('div', {'id':'fiche-seo-toaster-anchor'}).find_all('div', {'class':'toaster fiche-bloc-produit-item-b cursor-auto w100'}) else []
            residence = soupe.find('h1', {"id": "fiche-produit-residence-libelle"}).text.strip() \
                if soupe.find('h1', {"id": "fiche-produit-residence-libelle"}) else ''
            localisation = soupe.find('button', {"id": "fiche-produit-localisation"}).find('span', class_='fs-5').text.strip() \
                if soupe.find('button', {"id": "fiche-produit-localisation"}) else ''

            breadcrumbs = []
            
            try:
                breadcrumbs = soupe.find(
                    'ol', {'id': 'ui-ariane'}).find_all('li', {'itemprop': 'itemListElement'})
            except:
                breadcrumbs = soupe.find(
                    'nav', {'id': 'ui-ariane'}).find_all('div', {'itemprop': 'itemListElement'})

            station_breadcrumb = breadcrumbs[-2:-1][0].find('a', class_='ariane-item') if breadcrumbs[-2:-1][0].find('a', class_='ariane-item') else ''
            station_name = localisation
            station_key = station_breadcrumb['href'].split(',')[1].replace('.html', '') if station_breadcrumb != '' else ''

            if not station_key:
                station_key = self.stations[station_name.upper()] if station_name.upper() in self.stations.keys() else ''
                print(f"\t===> {station_name} =>  {station_key}")

            for toaster in toasters:
                is_disponible = False if toaster.find('div', {'class':'toaster-right fiche_produit_indispo'}) else True

                if is_disponible:
                    data = {}
                    date_price = self.week_scrap

                    typologie = toaster.find('div', class_="toaster-residence-libelle-container").text.strip().replace(',', '-').replace('/', ' ou ') \
                        if toaster.find('div', class_='toaster-residence-libelle-container') else ''

                    prix_actuel = toaster.find('span', {'class':'price_item_final'}).find('span').text.strip()[:-1] \
                        if toaster.find('span', {'class':'price_item_final'}).find('span') else 0.00

                    prix_init = toaster.find('span', {'class':'price_item_barre'}).text.strip()[:-1] \
                        if toaster.find('span', {'class':'price_item_barre'}) else prix_actuel
                    
                    link = toaster.find("div", class_="toaster-right-cta").find("a", href=True)['href'] \
                        if toaster.find("div", class_="toaster-right-cta") else ''


                    n_offres, date_debut, date_fin = link_params(link)
                    data['web-scrapper-order'] = ''
                    data['date_price'] = date_price
                    data['date_debut'] = date_debut
                    data['date_fin'] = date_fin
                    data['prix_init'] = prix_init
                    data['prix_actuel'] = prix_actuel
                    data['typologie'] = typologie
                    data['n_offre'] = n_offres
                    data['nom'] = remove_char(residence)
                    data['localite'] = remove_char(localisation)
                    data['date_debut-jour'] = ''
                    data['Nb semaines'] = datetime.strptime(date_debut, '%d/%m/%Y').isocalendar()[1]
                    data['cle_station'] = station_key
                    data['nom_station'] = station_name
                    data['url'] = link.replace('https://www.maeva.com', '')

                    invalid_fields, maeva_data_is_valid = Maeva_Field_Validator(data).is_valid()
                    if maeva_data_is_valid:
                        self.data_container.append(data)
                    else:
                        print(f"\t  ==> {invalid_fields}")

            table_fields = ['prix_init', 'prix_actuel', 'typologie','n_offre', 'nom', 'localite', 'cle_station', 'nom_station']

            if self.data_container:
                show_datatable(self.data_container, table_fields)


    def execute(self) -> None:
        self.setup_scrap()
        self.load_station_list()
        self.use_new_driver()
        self.get_dest_count(self.dest_file_path)
        self.load_history()
        try:
            for x in range(self.history['last_index'], self.dest_count):
                print(f"\t ===>  history {self.history['last_index']}/{self.dest_count}")
                self.set_url(x)
                self.goto_page(self.url)
                if self.page_is_checked():
                    self.extract_data()
                self.save_data()
                current_history = self.history
                self.history['last_index'] = current_history['last_index'] + 1
                self.set_history(self.history)
        except KeyboardInterrupt:
            sys.exit()


def main_arguments() -> object:

    def get_monday():
        return str((datetime.now() - timedelta(days = datetime.now().weekday())).strftime("%d/%m/%Y"))

    parser = argparse.ArgumentParser(description="Maeva program",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--platform', '-p', dest='platform',
                        default='maeva', help="Site source")
    parser.add_argument('--action', '-a', dest='action', default='',
                        help="""Tâche à faire: \n \t 'init': actualiser la liste des destinations. | 'start': Lancer le scraping des annonces. | 'clean': pour nettoyer le résultat""")
    parser.add_argument('--station', '-s', dest='station', default='', help="Nom du fichier contenant la liste des stations")
    parser.add_argument('--name', '-n', dest='name',
                        default='', help="Nom du fichier qui va contenir les donner")
    parser.add_argument('--start-date', '-b', dest='start_date',
                        default='', help="Date début format 'dd/mm/YYYY'")
    parser.add_argument('--end-date', '-e', dest='end_date',
                        default='', help="Date fin format 'dd/mm/YYYY'")
    parser.add_argument('--frequency', '-f', dest='frequency',
                        default='', help="Frequence du scrap \n \t '3' : pour frequence de 3 jours | '7' pour frequence de 7 jours | 'all' : pour tous les frequences")
    parser.add_argument('--week-scrap', '-w', dest='week_scrap', default=get_monday(), help="Date du lundi de la semaine à scraper format 'dd/mm/YYYY'")
    parser.add_argument('--destination', '-d', dest='destination', default='', help="Nom du fichier contenant la liste des destinations")
    return parser.parse_args()


ARGS_INFO = {
        '-a': {'long': '--action', 'dest': 'action', 'help': """Tâche à faire: \n \t
        'init': Récupération des urls à scraper. | 'start': Lancer le scraping des annonces. | 'clean': Nettoyer le résultat"""},
        '-d': {'long': '--destination', 'dest': 'destination', "help": "chemin du fichier contenant les destinations"},
        '-n': {'long': '--name', 'dest': 'name', "help": "Nom du fichier qui va contenir les donner"},
        '-w': {'long': '--week-scrap', 'dest': 'week_scrap', "help": "Date de la semaine de scrap"},
        '-s': {'long': '--station', 'dest': 'station', "help": "le nom du fichier station"},
        '-b': {'long': '--start-date', 'dest': 'start_date', "help": "Date debut"},
        '-e': {'long': '--end-date', 'dest': 'end_date', "help": "Date fin"},
    }

def check_arguments(args, required):
    miss = []

    for item in required:
        if not getattr(args, ARGS_INFO[item]['dest']):
            miss.append(f'{item} ou {ARGS_INFO[item]["long"]} ({ARGS_INFO[item]["help"]})')

    return miss


args = main_arguments()

if args.action and args.action == 'start':
    miss_command = check_arguments(args, ['-d', '-n', '-w'])
    if len(miss_command):
        raise Exception(f"Argument(s) manquant(s): {', '.join(miss_command)}")
    else:
        m = MaevaScraper(
        week_scrap=args.week_scrap,
        name=args.name,
        dest_name=args.destination,
        plateform='maeva'
        )
        m.execute()