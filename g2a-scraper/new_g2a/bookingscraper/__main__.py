from bookingscraper import BookingInitializer, BookingScraper
import argparse
from datetime import datetime, timedelta


def main_arguments() -> object:

    def get_monday():
        return str((datetime.now() - timedelta(days = datetime.now().weekday())).strftime("%d/%m/%Y"))

    parser = argparse.ArgumentParser(description="Booking program",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--platform', '-p', dest='platform',
                        default='booking', help="Site source")
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
        '-f': {'long': '--frequency', 'dest': 'frequency', "help": "Frequence de scrap"},
    }

def check_arguments(args, required):
    miss = []

    for item in required:
        if not getattr(args, ARGS_INFO[item]['dest']):
            miss.append(
                f'{item} ou {ARGS_INFO[item]["long"]} ({ARGS_INFO[item]["help"]})')

    return miss


args = main_arguments()

if args.action and args.action == 'start':
    miss_command = check_arguments(args, ['-d', '-n', '-w'])
    if len(miss_command):
        raise Exception(f"Argument(s) manquant(s): {', '.join(miss_command)}")
    else:
        b = BookingScraper(
            dest_name=args.destination,
            name=args.name,
            week_date=args.week_scrap
        )
        b.execute()
elif args.action and args.action == 'init':
    miss_command = check_arguments(args, ['-d', '-f', '-s', '-e'])
    if len(miss_command):
        raise Exception(f"Argument(s) manquant(s): {', '.join(miss_command)}")
    else:
        b = BookingInitializer(
            station_name=args.station,
            start_date=args.start_date,
            end_date=args.end_date,
            dest_name=args.destination,
            freq=int(args.frequency)
        )
        b.execute()


