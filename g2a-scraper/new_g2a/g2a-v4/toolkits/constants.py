from dotenv import load_dotenv
import os

load_dotenv()

PROJECT_FOLDER_PATH = os.environ.get("PROJECT_FOLDER_PATH")
LOG_FOLDER_PATH = os.environ.get("LOG_FOLDER_PATH")
STATION_FOLDER_PATH = os.environ.get("STATION_FOLDER_PATH")
DESTS_FOLDER_PATH = os.environ.get("DESTS_FOLDER_PATH")
OUTPUT_FOLDER_PATH = os.environ.get("OUTPUT_FOLDER_PATH")
BUG_FOLDER_PATH = os.environ.get("BUG_FOLDER_PATH")
G2A_API_URL = os.environ.get("G2A_API_URL")
G2A_API_TOKEN = os.environ.get("G2A_API_TOKEN")
PROTONVPN_CONNEXION_ID = os.environ.get("PROTONVPN_CONNEXION_ID")
NORDVPN_CONNEXION_ID = os.environ.get("NORDVPN_CONNEXION_ID")

BOOKING_CSV_FIELDS = [
    "web-scrapper-order",
    ""
]

MAEVA_CSV_FIELDS = [
    "web-scrapper-order",
    "date_price",
    "date_debut",
    "date_fin",
    "prix_init",
    "prix_actuel",
    "typologie",
    "n_offre",
    "nom",
    "localite",
    "date_debut-jour",
    "Nb semaines",
    "cle_station",
    "nom_station",
    "url"
]


CAMPING_CSV_FIELDS = [
    "web-scrapper-order",
    ""
]

EDOMIZIL_CSV_FIELDS = [
    "web-scrapper-order",
    ""
]

