from scraper import ListScraper
import argparse

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
    parser.add_argument('--establishments', '-e', dest='establishments', default=[], help="Liste des établissements à scaper uniquement pour les options 'by-establishment' et 'specified'.")
    parser.add_argument('--sites', '-s', dest='sites', default=[], help="Liste des sites à scaper uniquement pour les options 'by-website' et 'specified'.")
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
                sc.init()
                sc.start(args.sites.split(','))
            else:
                raise Exception(f"Argument(s) manquant(s): {', '.join(miss)}")
        if args.type == 'by-establishment':
            miss = check_arguments(args, ['-e'])
            if not len(miss):
                sc.init(args.establishments.split(','))
                sc.start(ALL_WEBSITES)
            else:
                raise Exception(f"Argument(s) manquant(s): {', '.join(miss)}")
        if args.type == 'specified':
            miss = check_arguments(args, ['-s', '-e'])
            if not len(miss):
                sc.init(args.establishments.split(','))
                sc.start(args.sites.split(','))
            else:
                raise Exception(f"Argument(s) manquant(s): {', '.join(miss)}")
        if args.type == 'auto':
            sc.init()
            sc.start(AUTO_WEBSITES)
        if args.type == 'manual':
            sc.init()
            sc.start(MANUAL_WEBSITES)
    
    else:
        raise Exception(f"Argument(s) manquant(s): {', '.join(miss)}")
