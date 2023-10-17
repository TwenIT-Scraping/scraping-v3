from scraper import ListScraper
import argparse
from datetime import datetime
import os
import dotenv

ALL_WEBSITES = [
    'booking',
    'maeva',
    'camping',
    'hotels',
    'google',
    'opentable',
    'trustpilot',
    'tripadvisor',
    'expedia'
]

AUTO_WEBSITES = [
    'booking',
    'maeva',
    'camping',
    'hotels',
    'google',
    'opentable',
    'trustpilot',
    'tripadvisor'
]

MANUAL_WEBSITES = [
    'expedia'
]


def main_arguments() -> object:
    parser = argparse.ArgumentParser(description="E-reputation program",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--type', '-t', dest='type', default='',
                        help="""Définir les sites à scraper. Options: all, by-website, by-establishment, specified, auto, manual""")
    parser.add_argument('--establishments', '-e', dest='establishments', default=[],
                        help="Liste des établissements à scaper uniquement pour les options 'by-establishment' et 'specified'.")
    parser.add_argument('--sites', '-s', dest='sites', default=[],
                        help="Liste des sites à scaper uniquement pour les options 'by-website' et 'specified'.")
    return parser.parse_args()


ARGS_INFO = {
    '-t': {'long': '--type', 'dest': 'type', 'help': "Définir les sites à scraper. Options: all, by-website, by-establishment, specified, auto, manual"},
    '-e': {'long': '--establishments', 'dest': 'establishments', "help": "Liste des établissements à scaper uniquement pour les options 'by-establishment' et 'specified'."},
    '-s': {'long': '--sites', 'dest': 'sites', "help": "Liste des sites à scaper uniquement pour les options 'by-website' et 'specified'."}
}


def check_arguments(args, required):
    miss = []

    for item in required:
        if not getattr(args, ARGS_INFO[item]['dest']):
            miss.append(
                f'{item} ou {ARGS_INFO[item]["long"]} ({ARGS_INFO[item]["help"]})')

    return miss


if __name__ == '__main__':

    dotenv.load_dotenv()

    history_filename = f'{os.environ.get("HISTORY_FOLDER")}/review-scraping-log.txt'

    now = datetime.now()
    if os.path.exists(history_filename):
        with open(history_filename, 'a', encoding='utf-8') as file:
            file.write("Démarrage scrap reviews: " +
                       now.strftime("%d/%m/%Y %H:%M:%S") + '\n')
    else:
        with open(history_filename, 'w', encoding='utf-8') as file:
            file.write("Démarrage scrap reviews: " +
                       now.strftime("%d/%m/%Y %H:%M:%S") + '\n')

    try:

        args = main_arguments()

        miss = check_arguments(args, ['-t'])

        if not len(miss):
            sc = ListScraper()

            if args.type == 'all':
                sc.init()
                sc.start(ALL_WEBSITES)
            if args.type == 'by-website':
                miss = check_arguments(args, ['-s'])
                if not len(miss):
                    with open(history_filename, 'a', encoding='utf-8') as file:
                        file.write(f" ({args.sites}) ")
                    sc.init()
                    sc.start(args.sites.split('|'))
                else:
                    raise Exception(
                        f"Argument(s) manquant(s): {', '.join(miss)}")
            if args.type == 'by-establishment':
                miss = check_arguments(args, ['-e'])
                if not len(miss):
                    with open(history_filename, 'a', encoding='utf-8') as file:
                        file.write(f" ({args.establishments}) ")
                    sc.init(args.establishments.split('|'))
                    sc.start(ALL_WEBSITES)
                else:
                    raise Exception(
                        f"Argument(s) manquant(s): {', '.join(miss)}")
            if args.type == 'specified':
                miss = check_arguments(args, ['-s', '-e'])
                if not len(miss):
                    with open(history_filename, 'a', encoding='utf-8') as file:
                        file.write(f" ({args.establishments}: {args.sites}) ")
                    sc.init(args.establishments.split('|'))
                    sc.start(args.sites.split('|'))
                else:
                    raise Exception(
                        f"Argument(s) manquant(s): {', '.join(miss)}")
            if args.type == 'auto':
                with open(history_filename, 'a', encoding='utf-8') as file:
                    file.write(" (auto) ")
                sc.init()
                sc.start(AUTO_WEBSITES)
            if args.type == 'manual':
                with open(history_filename, 'a', encoding='utf-8') as file:
                    file.write(" (auto) ")
                sc.init()
                sc.start(MANUAL_WEBSITES)

            now = datetime.now()
            with open(history_filename, 'a', encoding='utf-8') as file:
                file.write("  ===>  Fin scrap reviews: " +
                           now.strftime("%d/%m/%Y %H:%M:%S") + '\n')

        else:
            raise Exception(f"Argument(s) manquant(s): {', '.join(miss)}")
    except Exception as e:
        now = datetime.now()
        with open(history_filename, 'a', encoding='utf-8') as file:
            file.write("  ===>  Fin scrap meteo WITH ERRORS: " +
                       now.strftime("%d/%m/%Y %H:%M:%S") + ':' + e + '\n')
