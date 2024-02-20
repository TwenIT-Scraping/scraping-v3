from scraper import ListScraper
import argparse
from datetime import datetime
import os
import dotenv


def main_arguments() -> object:
    parser = argparse.ArgumentParser(description="E-reputation program",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--type', '-t', dest='type', default='',
                        help="""Définir les sites à scraper. Options: all, by-website, by-establishment, specified""")
    parser.add_argument('--establishments', '-e', dest='establishments', default=[],
                        help="Liste des établissements à scaper uniquement pour les options 'by-establishment' et 'specified'.")
    parser.add_argument('--sites', '-s', dest='sites', default=[],
                        help="Liste des sites à scaper uniquement pour les options 'by-website' et 'specified'.")
    parser.add_argument('--name', '-n', dest='name', default="",
                        help="Nom du fichier à traiter.")
    parser.add_argument('--auto-save', '-a', dest='auto_save',
                        default="1", choices=["0", "1"], help="Uploader tout de suite les résultats.")
    return parser.parse_args()


ARGS_INFO = {
    '-t': {'long': '--type', 'dest': 'type', 'help': "Définir les sites à scraper. Options: all, by-website, by-establishment, specified, auto, manual"},
    '-e': {'long': '--establishments', 'dest': 'establishments', "help": "Liste des établissements à scaper uniquement pour les options 'by-establishment' et 'specified'."},
    '-s': {'long': '--sites', 'dest': 'sites', "help": "Liste des sites à scaper uniquement pour les options 'by-website' et 'specified'."},
    '-n': {'long': '--name', 'dest': 'name', "help": "Nom du fichier à traiter."},
    '-a': {'long': '--auto-save', 'dest': 'auto_save', "help": "Uploader tout de suite les résultats."}
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

    print("lancement")

    try:

        args = main_arguments()

        miss = check_arguments(args, ['-t'])

        if not len(miss):

            sc = ListScraper()

            if args.type == 'list':
                print(sc.get_providers())

            if args.type == 'prepare-all':
                sc.transform_all_data()

            if args.type == 'prepare-once':
                sc.transform_data(args.name)

            if args.type == 'upload-all':
                sc.upload_all_results()

            if args.type == 'upload-once':
                sc.upload_data(args.name)

            if args.type == 'all':
                sc.init()
                sc.start()

            if args.type == 'by-website':
                miss = check_arguments(args, ['-s'])
                if not len(miss):
                    with open(history_filename, 'a', encoding='utf-8') as file:
                        file.write(f" ({args.sites}) ")

                    if args.auto_save == "1":
                        sc.set_auto_save()

                    for s in args.sites.split('|'):
                        print("Site: ", s)
                        sc.init(source=s)
                        sc.start()
                else:
                    raise Exception(
                        f"Argument(s) manquant(s): {', '.join(miss)}")

            if args.type == 'by-establishment':
                miss = check_arguments(args, ['-e'])
                if not len(miss):
                    with open(history_filename, 'a', encoding='utf-8') as file:
                        file.write(f" ({args.establishments}) ")

                    if args.auto_save == "1":
                        sc.set_auto_save()

                    for e in args.establishments.split('|'):
                        sc.init(ename=e)
                        sc.start()
                else:
                    raise Exception(
                        f"Argument(s) manquant(s): {', '.join(miss)}")

            if args.type == 'specified':
                miss = check_arguments(args, ['-s', '-e'])
                if not len(miss):
                    with open(history_filename, 'a', encoding='utf-8') as file:
                        file.write(f" ({args.establishments}: {args.sites}) ")

                    if args.auto_save == "1":
                        sc.set_auto_save()

                    sc.init(source=args.sites, ename=args.establishments)
                    sc.start()
                else:
                    raise Exception(
                        f"Argument(s) manquant(s): {', '.join(miss)}")

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
                       now.strftime("%d/%m/%Y %H:%M:%S") + ':' + str(e) + '\n')
