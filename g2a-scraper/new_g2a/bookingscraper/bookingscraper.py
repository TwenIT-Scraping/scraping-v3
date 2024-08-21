from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from dotenv import load_dotenv
from random import randint
import pandas as pd 
import re, os, time, sys, csv, json

from toolkit import ordergenerator as og
from toolkit import general_tools as gt
from toolkit import changeip



load_dotenv()


OUTPUT_FOLDER_PATH = os.environ.get('OUTPUT_FOLDER_PATH')
STATION_FOLDER_PATH = os.environ.get('STATION_FOLDER_PATH')
DESTINATION_PATH = os.environ.get('DESTINATION_PATH')
BUG_TRACK_PATH = os.environ.get('BUG_TRACK_PATH')
LOGS_FOLDER_PATH = os.environ.get('LOGS_FOLDER_PATH')

FILED_NAMES = [
                'web-scraper-order',
                'date_price',
                'date_debut', 
                'date_fin',
                'prix_init',
                'prix_actuel',
                'typologie',
                'n_offre',
                'nom',
                'localite',
                'date_debut-jour',
                'Nb semaines'
            ] 

class BookingInitializer(object):

    def __init__(self, station_name:str, start_date:str, end_date:str, freq:int, dest_name:str) -> None:
        self.station_name = station_name
        self.start_date = datetime.strptime(start_date, "%d/%m/%Y")
        self.end_date = datetime.strptime(end_date, "%d/%m/%Y")
        self.freq = freq
        self.dest_name = dest_name
        self.dest_url = []


    def load_stations(self) -> list | None:
        global STATION_FOLDER_PATH
        f""" load stations urls in json file from {STATION_FOLDER_PATH} and return it as list """
        print(" ==> reading station file")
        time.sleep(1)
        # try:
        station_url = json.load(open(f"{STATION_FOLDER_PATH}/{self.station_name}"))
        return station_url
        # except FileNotFoundError:
        #     show_message("File not found", "File not found or station file name incorrect", "error")
        #     sys.exit()

    def normalize_url_params(self, url:str, start:str, end:str) -> str:
        """ normalize url parameters as needed for data scraping format """
        print(url)
        url_params = parse_qs(urlparse(url).query)
        if "lang" not in url_params:
            url += f"&lang=fr"
        if "checkin" not in url_params:
            url += f"&checkin={start}"
        if "checkout" not in url_params:
            url += f"&checkout={end}"
        if "selected_currency" not in url_params:
            url += "&selected_currency=EUR"
        return url

    def generate_url(self, stations_url:list) -> list:
        """generate dynamic urls for any station between interval of given dates {start_date and end_date}"""
        time.sleep(1)
        correct_dest_url = []
        if self.freq in [1, 3, 7]:
            date_space = int((self.end_date - self.start_date).days) + 1
            checkin = self.start_date
            checkout = checkin + timedelta(days=self.freq)  

            for _ in range(date_space):
                for station_url in stations_url:
                    url = self.normalize_url_params(station_url, checkin.strftime("%Y-%m-%d"), checkout.strftime("%Y-%m-%d"))
                    correct_dest_url.append(url)
                checkin += timedelta(days=1)
                checkout += timedelta(days=1)

            return correct_dest_url

        else:
            gt.show_message('Frequency not regular', "scrap frequency should be 1 or 3 or 7", 'error')

    def save_destination(self, data:list) -> None:
        """save destination urls in to json file"""
        print(" ==> saving destination")
        global DESTINATION_PATH
        folder_path = f"{DESTINATION_PATH}/{self.start_date.strftime('%d_%m_%Y')}"

        print(folder_path)

        dest_name = f"{folder_path}/{self.dest_name}.json"
        print(dest_name)
        if not Path(folder_path).exists():
            os.makedirs(folder_path)
        if not Path(dest_name).exists():
            with open(dest_name, "w") as openfile:
                openfile.write(json.dumps(data, indent=4))
        else:
            print(f"  ==> Destination with name {self.dest_name}.json already exist, do you want to overwrite this ? yes or no")
            response = input("  ==> your answer :")
            while response not in ['yes', 'no']:
                print(' ==> response unknown, please give correct answer!')
                print(f"  ==> Destination with name {self.dest_name}.json already exist, do you want to overwrite this ? yes or no")
                response = input("  ==> your answer :")
            match response:
                case 'yes':
                    with open(dest_name, "w") as openfile:
                        openfile.write(json.dumps(data))
                case 'no':
                    print(f'  ==> Destination {self.dest_name}.json kept')

        number_of_dest = len(json.load(open(dest_name)))

        print(f" ==> well done, {number_of_dest} destinations saved!")


    def execute(self) -> None:
        """ running Booking initalizer to setup booking scraping """
        print(" ==> initializing booking scraper ...")
        global BUG_TRACK_PATH
        stations = self.load_stations()
        new_correct_url = self.generate_url(stations)
        self.dest_url += new_correct_url

        self.save_destination(self.dest_url)


class OldBookingScraper(object):

    def __init__(self, dest_name:str, name:str, week_date:str) -> None:

        self.dest_name = dest_name
        self.name = name

        self.destinations = []
        self.history = {}
        self.week_scrap = datetime.strptime(week_date, "%d/%m/%Y").strftime("%d_%m_%Y")
        self.exception_count = 0
        self.code = og.create_code()
        self.order_index = 1
        self.driver_cycle = 0

        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        # self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--incognito')
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.maximize_window()

    def create_log(self) -> None:
        print("  ==> creating log")
        log = { "last_index": 0, "week_scrap": self.week_scrap }
        if not Path(f"{LOGS_FOLDER_PATH}/{self.week_scrap}").exists():
            os.makedirs(f"{LOGS_FOLDER_PATH}/{self.week_scrap}")
        gt.create_log_file(log_file_path=f"{LOGS_FOLDER_PATH}/{self.week_scrap}/{self.name}.json", log_value=log)

    def load_destinations(self) -> None:
        print("  ==> loading all destinations")
        self.destinations = gt.load_json(f"{DESTINATION_PATH}/{self.week_scrap}/{self.dest_name}")

        print(f"  ==> {len(self.destinations)} destination loaded")

    def load_history(self) -> None:
        print("  ==> loading history")
        self.history = gt.load_json(f"{LOGS_FOLDER_PATH}/{self.week_scrap}/{self.name}.json")
        self.week_scrap = self.history['week_scrap']

    def set_history(self) -> None:
        current_dest = self.history['last_index']
        self.history['last_index'] = current_dest + 1
        gt.save_history(f"{LOGS_FOLDER_PATH}/{self.week_scrap}/{self.name}.json", self.history)
        print('  ==> set history')

    def use_new_driver(self) -> None:
        time.sleep(1)
        try:
            self.driver.quit()
        except:
            pass
        self.driver = webdriver.Chrome(self.chrome_options)
        self.driver_cycle = 0


    def close_modal(self) -> None:
        try:
            if self.driver.find_element(By.ID, 'onetrust-accept-btn-handler'):
                self.driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()
        except:
            pass

    def goto_page(self, url:str) -> None:
        print(f"  ==> load page {url}")
        if self.exception_count == 15:
            gt.show_message("Timeout Exception Error", "max exception reached, please check it before continue", "warning")
        if self.driver_cycle == 10:
            self.driver.close()
            # changeip.refresh_connection()
            self.use_new_driver()
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 1)
            self.close_modal()
            self.exception_count = 0
        except TimeoutException as e:
            gt.report_bug(f"{BUG_TRACK_PATH}/bug_{self.week_scrap}.txt", {"error": e, "bug_url":self.driver.current_url})
            time.sleep(2)
            self.exception_count += 1
            self.use_new_driver()
            self.goto_page(url)


    def get_all_pages(self) -> object:
        yield {'url':self.driver.current_url, 'page':self.driver.page_source}
        while True:
            soupe = BeautifulSoup(self.driver.page_source, 'lxml')
            next_button = soupe.find('button', {'arial-label':'Page suivante', 'disabled':False})
            if next_button:
                next_page = self.driver.find_element(By.XPATH, "//button[@aria-label='Page suivante]")
                self.driver.execute_script("arguments[0].click();", next_page)
                WebDriverWait(self.driver, 2)
                yield {'url':self.driver.current_url, 'page':self.driver.page_source}
            else:
                yield {'url':self.driver.current_url, 'page':self.driver.page_source}
                break
        

    def create_output_file(self) -> None:
        global FILED_NAMES
        if not Path(f"{OUTPUT_FOLDER_PATH}/{self.week_scrap}").exists():
            os.makedirs(f"{OUTPUT_FOLDER_PATH}/{self.week_scrap}")
        gt.create_file(f"{OUTPUT_FOLDER_PATH}/{self.week_scrap}/{self.name}.csv", FILED_NAMES)


    def get_dates(self, url:str) -> tuple:
            """ function to get dates in url """
            url_params = parse_qs(urlparse(url).query)
            sep = '/'
            try:
                return sep.join(url_params['checkin'][0].split('-')[::-1]), sep.join(url_params['checkout'][0].split('-')[::-1])
            except KeyError:
                return f"{url_params['checkin_monthday'][0]}/{url_params['checkin_month'][0]}/{url_params['checkin_year'][0]}", f"{url_params['checkout_monthday'][0]}/{url_params['checkout_month'][0]}/{url_params['checkout_year'][0]}"

            
    def extract_data(self) -> list:
        print("  ==> extracting data")
        data_container = []

        page = 1
        while True:
            time.sleep(randint(1, 2))
            soupe = BeautifulSoup(self.driver.page_source.encode('utf-8').decode('utf-8'), 'html.parser')
            cards = []
            try:
                cards = soupe.find_all('div', {'data-testid':"property-card"})
            except:
                pass
            
            
            if len(cards) > 0:
                print(f"    ==> page {page}")
                for card in cards:
                    try:

                        nom = card.find('div', {'data-testid':"title"}).text.replace('\n', '').replace(',', '-').replace('"', "'") \
                            if card.find('div', {'data-testid':"title"}) else ''

                        localite = card.find('span', {'data-testid':"address"}).text.replace('\n', '') \
                            if card.find('span', {'data-testid':"address"}) else ''

                        taxe_text = card.find('div', {'data-testid':"availability-rate-information"}).find('div', {'data-testid':'taxes-and-charges'}).text[1:].replace(u'\xa0', u'').replace(' ', '')
                        taxe = int(''.join(list(filter(str.isdigit, taxe_text)))) if '€' in taxe_text else 0

                        prix_actuel = 0
                        prix_init = 0 
                        if card.find('span', {'data-testid':'price-and-discounted-price'}):
                            prix_actuel = card.find('div', {'data-testid':"availability-rate-information"}).find('span', {'data-testid':'price-and-discounted-price'}).text[1:].replace(u'\xa0', u'').replace(',', '').replace(' ', '')
                            prix_actuel = int(prix_actuel) + taxe
                            prix_init = card.find('div', {'data-testid':"availability-rate-information"}).find('div', {'tabindex':'0'}).find('span', {'class':'f018fa3636 d9315e4fb0'}).text[1:].replace(u'\xa0', u'').repalce(' ', '').repalce(',', '')\
                                if card.find('div', {'data-testid':"availability-rate-information"}).find('div', {'tabindex':'0'}).find('span', {'class':'f018fa3636 d9315e4fb0'}) else 0
                            prix_init = int(prix_init) + taxe if int(prix_init) > 0 else prix_actuel

                        elif card.find('span', class_='fcab3ed991') and prix_actuel == 0:
                            prix_actuel = int(card.find('span', class_='fcab3ed991').text[1:].replace(u'\xa0', u'').replace(',', '').replace(' ', '')) \
                                if card.find('span', class_='fcab3ed991') else 0
                            prix_actuel = prix_actuel + taxe
                            prix_init = card.find('span', class_='c5888af24f').text[1:].replace(u'\xa0', u'').replace(',', '').replace(' ', '') \
                                if card.find('span', class_='c5888af24f') else 0
                            prix_init = int(prix_init) + taxe if int(prix_init) > 0 else prix_actuel

                        elif prix_actuel == 0:
                            prix_actuel = int(card.find('div', {'data-testid':"availability-rate-information"}).find('span', {'data-testid':'price-and-discounted-price'}).text[1:].replace(u'\xa0', u'').replace(',', '').replace(' ', '')) \
                                if card.find('div', {'data-testid':"availability-rate-information"}).find('span', {'data-testid':'price-and-discounted-price'}) else 0
                            prix_actuel = prix_actuel + taxe
                            prix_init = int(card.find('div', {'data-testid':"availability-rate-information"}).find('span', class_='e729ed5ab6').text[1:].replace(u'\xa0', u'').replace(',', '').replace(' ', '')) \
                                if card.find('div', {'data-testid':"availability-rate-information"}).find('span', class_='e729ed5ab6') else 0
                            prix_init = int(prix_init) + taxe if int(prix_init) > 0 else prix_actuel

                        typologie = ''
                        if card.find('div', {'data-testid':"recommended-units"}):
                            typologie = card.find('div', {'data-testid':"recommended-units"}).find('h4').text.strip().replace('\n', '').replace(u'\xa0', ' ') \
                                if card.find('div', {'data-testid':'recommended-units'}).find('h4') else ""

                        date_prix = (datetime.now() + timedelta(days=-datetime.now().weekday())).strftime('%d/%m/%Y')
                        date_debut, date_fin = self.get_dates(self.driver.current_url)
                        data_container.append({
                            'nom': nom,
                            'n_offre': '',
                            'date_debut': date_debut,
                            'date_fin': date_fin,
                            'localite': localite,
                            'prix_actuel': prix_actuel,
                            'prix_init': prix_init,
                            'typologie': typologie,
                            'date_price': date_prix,
                            'Nb semaines': datetime.strptime(date_debut, '%d/%m/%Y').isocalendar()[1],
                            'date_debut-jour': '',
                            'web-scraper-order': og.get_fullcode(self.code, self.order_index)
                        })

                        print({
                            'nom': nom,
                            'n_offre': '',
                            'date_debut': date_debut,
                            'date_fin': date_fin,
                            'localite': localite,
                            'prix_actuel': prix_actuel,
                            'prix_init': prix_init,
                            'typologie': typologie,
                            'date_price': date_prix,
                            'Nb semaines': datetime.strptime(date_debut, '%d/%m/%Y').isocalendar()[1],
                            'date_debut-jour': '',
                            'web-scraper-order': og.get_fullcode(self.code, self.order_index)
                        })
                    except AttributeError:
                        pass

                    self.order_index += 1 
                next_btn = soupe.find('button', {'aria-label':"Page suivante"})
                if next_btn:
                    try:
                        if not self.driver.find_element(By.XPATH, "//button[@aria-label='Page suivante']").get_property('disabled'):
                            page += 1
                            self.driver.find_element(By.XPATH, "//button[@aria-label='Page suivante']").click()
                            WebDriverWait(self.driver, 1)
                        else:
                            page = 1
                            break
                    except:
                        break
                else:
                    break
            else:
                break


        return data_container
    

    def execute(self) -> None:
        global FILED_NAMES
        print("  ==> scraping start")
        self.create_log()
        self.create_output_file()
        self.load_destinations()
        self.load_history()
        if self.destinations:
            for x in range(self.history['last_index'], len(self.destinations)):
                print(f"  ==> {self.history['last_index'] + 1} / {len(self.destinations)}")
                self.goto_page(self.destinations[x])
                data_container = self.extract_data()
                print(data_container)
                print(f"  ==> {len(data_container)} data extracted ")
                gt.save_data(f"{OUTPUT_FOLDER_PATH}/{self.week_scrap}/{self.name}.csv", data_container, FILED_NAMES)

                self.set_history()
                self.driver_cycle += 1
            print("  ==> scrap finished")
        else:
            print("  ==> destination empty! ")


class BookingScraper(object):

    "last update 17/07/2024"

    def __init__(self, dest_name:str, name:str, week_date:str) -> None:

        self.dest_name = dest_name
        self.name = name

        self.destinations = []
        self.history = {}
        self.week_scrap = datetime.strptime(week_date, "%d/%m/%Y").strftime("%d_%m_%Y")
        self.exception_count = 0
        self.code = og.create_code()
        self.order_index = 1
        self.driver_cycle = 0

        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        # self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--incognito')
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.maximize_window()

    def create_log(self) -> None:
        print("  ==> creating log")
        log = { "last_index": 0, "week_scrap": self.week_scrap }
        if not Path(f"{LOGS_FOLDER_PATH}/{self.week_scrap}").exists():
            os.makedirs(f"{LOGS_FOLDER_PATH}/{self.week_scrap}")
        gt.create_log_file(log_file_path=f"{LOGS_FOLDER_PATH}/{self.week_scrap}/{self.name}.json", log_value=log)

    def load_destinations(self) -> None:
        print("  ==> loading all destinations")
        self.destinations = gt.load_json(f"{DESTINATION_PATH}/{self.week_scrap}/{self.dest_name}.json")

        print(f"  ==> {len(self.destinations)} destination loaded")

    def load_history(self) -> None:
        print("  ==> loading history")
        self.history = gt.load_json(f"{LOGS_FOLDER_PATH}/{self.week_scrap}/{self.name}.json")
        self.week_scrap = self.history['week_scrap']

    def set_history(self) -> None:
        current_dest = self.history['last_index']
        self.history['last_index'] = current_dest + 1
        gt.save_history(f"{LOGS_FOLDER_PATH}/{self.week_scrap}/{self.name}.json", self.history)
        print('  ==> set history')

    def use_new_driver(self) -> None:
        time.sleep(1)
        try:
            self.driver.close()
            self.driver.quit()
        except:
            pass
        self.driver = webdriver.Chrome(self.chrome_options)
        self.driver.maximize_window()
        self.driver_cycle = 0

    def close_modal(self) -> None:
        try:
            if self.driver.find_element(By.ID, 'onetrust-accept-btn-handler'):
                self.driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()
                print("button1 clicked")
        except:
            pass
        try:
            if self.driver.find_element(By.XPATH, "//button[@aria-label='Ignorer les infos relatives à la connexion']"):
                self.driver.find_element(By.XPATH, "//button[@aria-label='Ignorer les infos relatives à la connexion']").click()
                print("button2 clicked")
        except:
            pass
        try:
            if self.driver.find_element(By.CSS_SELECTOR, "dba1b3bddf.e99c25fd33.aabf155f9a.f42ee7b31a.a86bcdb87f.b02ceec9d7"):
                self.driver.find_element(By.CSS_SELECTOR, "dba1b3bddf.e99c25fd33.aabf155f9a.f42ee7b31a.a86bcdb87f.b02ceec9d7").click()
                print("button3 clicked")
        except:
            pass



    def goto_page(self, url:str) -> None:
        print(f"  ==> load page {url}")
        if self.exception_count == 10:
            gt.show_message("Timeout Exception Error", "max exception reached, please check it before continue", "warning")
        if self.driver_cycle == 15:
            self.driver.close()
            # changeip.refresh_connection()
            self.use_new_driver()
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 1)
            self.close_modal()
            self.exception_count = 0
        except Exception as e:
            gt.report_bug(f"{BUG_TRACK_PATH}/bug_{self.week_scrap}.txt", {"error": e, "bug_url":self.driver.current_url})
            time.sleep(2)
            self.exception_count += 1
            self.use_new_driver()
            self.goto_page(url)
        
    def create_output_file(self) -> None:
        global FILED_NAMES
        if not Path(f"{OUTPUT_FOLDER_PATH}/{self.week_scrap}").exists():
            os.makedirs(f"{OUTPUT_FOLDER_PATH}/{self.week_scrap}")
        gt.create_file(f"{OUTPUT_FOLDER_PATH}/{self.week_scrap}/{self.name}.csv", FILED_NAMES)

    def get_dates(self, url:str) -> tuple:
            """ function to get dates in url """
            url_params = parse_qs(urlparse(url).query)
            sep = '/'
            try:
                return sep.join(url_params['checkin'][0].split('-')[::-1]), sep.join(url_params['checkout'][0].split('-')[::-1])
            except KeyError:
                return f"{url_params['checkin_monthday'][0]}/{url_params['checkin_month'][0]}/{url_params['checkin_year'][0]}", f"{url_params['checkout_monthday'][0]}/{url_params['checkout_month'][0]}/{url_params['checkout_year'][0]}"

    def get_cards(self) -> tuple:
        card_count = 0
        cards = []
        try:
            cards = self.driver.find_elements(By.XPATH, "//div[@data-testid='property-card']")
            card_count = len(cards)
            return cards, card_count 
        except NoSuchElementException:
            return cards, card_count 

    def scroll_to_last_card(self) -> None:
        self.close_modal()
        cards, count = self.get_cards()
        if cards:
            try:
                self.driver.execute_script('arguments[0].scrollIntoView({ behavior: "smooth", block: "center", inline: "center" })', cards[-1])
            except:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(3)

    def scroll_down(self):
        self.close_modal()
        cards, current_card_count = self.get_cards()
        if cards:
            self.scroll_to_last_card()
            while True:
                cards, new_card_count = self.get_cards()
                if new_card_count == current_card_count:
                    break
                if new_card_count > current_card_count:
                    self.scroll_to_last_card()
                current_card_count = new_card_count

    def load_page_content(self):
        self.scroll_down()
        while True:
            try:
                btn_vew_more = self.driver.find_element(By.XPATH, '//span[contains(text(), "Afficher plus de résultats") or contains(text(), "Load more results")]')
                if btn_vew_more:
                    self.driver.execute_script('arguments[0].scrollIntoView({ behavior: "smooth", block: "center", inline: "center" })', btn_vew_more)
                    time.sleep(1)
                    try:
                        btn_vew_more.click()
                    except:
                        pass
            except NoSuchElementException:
                print("\t ===> page loaded")
                break

        soupe = BeautifulSoup(self.driver.page_source, 'lxml')
        print(f"""\t===>  card diplayed : {len(soupe.find_all('div', {'data-testid':"property-card"}))}""")

    def is_valid_data(self, data:dict) -> bool:
        for key in data.keys():
            if key in ['n_offre', 'date_debut-jour']:
                continue
            if not data[key] or data[key] is None or data[key] == '':
                return False
            if key == 'prix_init' or key == 'prix_actuel':
                try:
                    float(data[key])
                except:
                    print('prix init or actuel invalid')
                    return False
        return True

    def extract_data(self) -> list:
        print("  ==> extracting data")
        data_container = []
        soupe = BeautifulSoup(self.driver.page_source.encode('utf-8').decode('utf-8'), 'html.parser')
        cards = []
        try:
            cards = soupe.find_all('div', {'data-testid':"property-card"})
        except:
            pass
        if len(cards) > 0:
            print(f"  \t==> {len(cards)} cards found")
            for card in cards:
                try:
                    nom = card.find('div', {'data-testid':"title"}).text.replace('\n', '').replace(',', '-').replace('"', "'") \
                        if card.find('div', {'data-testid':"title"}) else ''
                    localite = card.find('span', {'data-testid':"address"}).text.replace('\n', '') \
                        if card.find('span', {'data-testid':"address"}) else ''

                    taxe_text = card.find('div', {'data-testid':"availability-rate-information"}).find('div', {'data-testid':'taxes-and-charges'}).text[1:].replace(u'\xa0', u'').replace(' ', '')
                    taxe = int(''.join(list(filter(str.isdigit, taxe_text)))) if '€' in taxe_text else 0
                    prix_init = 0
                    prix_actual = 0
                    try:
                        prix_actual = int(card.find('div', {'data-testid':"availability-rate-information"}).find('span', {'data-testid':'price-and-discounted-price'}).text[1:].replace(u'\xa0', u'')) \
                            if card.find('div', {'data-testid':"availability-rate-information"}).find('span', {'data-testid':'price-and-discounted-price'}) else 0
                        if prix_actual and prix_actual > 0:
                            prix_actual += taxe
                    except:
                        print('prix actuel not found')
                    try:
                        prix_init = int(card.find('div', {'data-testid':"availability-rate-information"}).find('div', {'tabindex':'0'}).find('span', {'class':'f018fa3636 d9315e4fb0'}).text[1:].replace(u'\xa0', u'')) \
                            if card.find('div', {'data-testid':"availability-rate-information"}).find('div', {'tabindex':'0'}).find('span', {'class':'f018fa3636 d9315e4fb0'}) else 0
                        if prix_init and prix_init > 0:
                            prix_init += taxe
                    except:
                        prix_init = prix_actual
                        
                    typologie = card.find('h4').text.replace(u'\xa0', ' ').replace('\n', '') 
                    date_prix = (datetime.now() + timedelta(days=-datetime.now().weekday())).strftime('%d/%m/%Y')
                    date_debut, date_fin = self.get_dates(self.driver.current_url)
                    
                    data = {
                        'nom': nom,
                        'n_offre': '',
                        'date_debut': date_debut,
                        'date_fin': date_fin,
                        'localite': localite,
                        'prix_actuel': prix_actual,
                        'prix_init': prix_init,
                        'typologie': typologie,
                        'date_price': date_prix,
                        'Nb semaines': datetime.strptime(date_debut, '%d/%m/%Y').isocalendar()[1],
                        'date_debut-jour': '',
                        'web-scraper-order': og.get_fullcode(self.code, self.order_index)
                    }

                    if self.is_valid_data(data):
                        data_container.append(data)
                    else:
                        print(f'invalid data for {data}')
                except:
                    print('failed to extract')
                    pass
        return data_container
    
    def execute(self) -> None:
        global FILED_NAMES
        print("  ==> scraping start")
        self.create_log()
        self.create_output_file()
        self.load_destinations()
        self.load_history()
        if self.destinations:
            for x in range(self.history['last_index'], len(self.destinations)):
                print(f"  ==> {self.history['last_index'] + 1} / {len(self.destinations)}")
                self.goto_page(self.destinations[x])
                self.load_page_content()
                data_container = self.extract_data()
                print(data_container)
                print(f"  ==> {len(data_container)} data extracted ")
                gt.save_data(f"{OUTPUT_FOLDER_PATH}/{self.week_scrap}/{self.name}.csv", data_container, FILED_NAMES)
                self.set_history()
                self.driver_cycle += 1
            print("  ==> scrap finished")
        else:
            print("  ==> destination empty! ")

