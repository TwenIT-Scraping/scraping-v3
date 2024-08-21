import sys
import time
import pandas as pd
from abc import abstractmethod
from pathlib import Path

from toolkits import constants
from toolkits.ip_status_manager import get_status
from toolkits.file_manager import resolve_folder_path, write_json_file, read_json_file, write_csv_file

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import Fore

from toolkits.logger import clear_logs

class BaseScraping(object):

    def __init__(self, week_scrap:str, name:str, plateform:str) -> None:
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--incognito')
        self.chrome_options.add_extension('./canvas_blocker_0_2_0_0.crx')

        self.week_scrap = week_scrap
        self.name = name
        self.plateform = plateform

        self.max_driver_cycle = 25
        self.driver_cycle = 1
        self.history = {}
        self.destinations = []
        self.urls = []
        self.data_container = []
        self.log_count = 0

        self.bug_folder = f"{constants.BUG_FOLDER_PATH}/{self.plateform}/{'_'.join(self.week_scrap.split('/'))}"
        self.log_folder = f"{constants.LOG_FOLDER_PATH}/{self.plateform}/{'_'.join(self.week_scrap.split('/'))}"
        self.output_folder = f"{constants.OUTPUT_FOLDER_PATH}/{self.plateform}/{'_'.join(self.week_scrap.split('/'))}"
        self.bug_file_path = f"{constants.BUG_FOLDER_PATH}/{self.plateform}/bug_{'_'.join(self.week_scrap.split('/'))}.json"
        self.log_file_path = f"{constants.LOG_FOLDER_PATH}/{self.plateform}/{'_'.join(self.week_scrap.split('/'))}/log_{self.name}.json"
        self.output_file_path = f"{constants.OUTPUT_FOLDER_PATH}/{self.plateform}/{'_'.join(self.week_scrap.split('/'))}/result_{self.name}.csv"

    def set_driver_in_background(self) -> None:
            self.chrome_options.add_argument('--headless')

    def use_new_driver(self) -> None:
        try:
            self.driver.close()
            self.driver.quit()
        except:
            pass
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.maximize_window()
        self.driver_cycle = 0

    def check_ip_status(self) -> None:
        try:
            while True:
                ip_status = get_status('STATUS')
                if ip_status == 'activated':
                    print("\t ===> connexion is enabled ...")
                    break
                else:
                    print("\t ===> connexion is disabled ...", end='\r')
                print("\t ===> waiting for connexion ...", end='\r')
                time.sleep(3)
        except KeyboardInterrupt:
            sys.exit()

    def goto_page(self, url:str) -> None:
        if self.log_count > 5:
            clear_logs()
            self.log_count = 0
        self.check_ip_status()
        try:
            if self.driver_cycle > self.max_driver_cycle:
                self.use_new_driver()
            self.driver.get(url)
            print(Fore.GREEN + f"\t url  ==> {url}")
            WebDriverWait(self.driver, timeout=10)
        except:
            self.check_ip_status()
            self.goto_page(url)
        self.driver_cycle += 1
        self.log_count += 1
        time.sleep(.5)

    def reload_page(self) -> None:
        self.driver.execute("window.location.reload();")

    def create_base_folders(self) -> None:
        scrap_base_folders = [
            self.bug_folder, 
            self.log_folder, 
            self.output_folder
        ]
        for path in scrap_base_folders:
            resolve_folder_path(path)

    def create_files(self) -> None:
        self.create_log_file()
        match self.plateform:
            case 'maeva':
                pd.DataFrame(columns=constants.MAEVA_CSV_FIELDS).to_csv(self.output_file_path, index=False)
            case 'camping':
                pd.DataFrame(columns=constants.CAMPING_CSV_FIELDS).to_csv(self.output_file_path, index=False)
            case 'booking':
                pd.DataFrame(columns=constants.BOOKING_CSV_FIELDS).to_csv(self.output_file_path, index=False)
            case 'edomizil':
                pd.DataFrame(columns=constants.EDOMIZIL_CSV_FIELDS).to_csv(self.output_file_path, index=False)

    def create_log_file(self) -> None:
        logs = {"last_index": 0}
        if not Path(self.log_file_path).exists():
            write_json_file(self.log_file_path, logs)

    def load_history(self) -> None:
        self.history = read_json_file(self.log_file_path)
        print(f'history: {self.history}')

    def set_history(self, new_history:dict) -> None:
        write_json_file(self.log_file_path, new_history)
        self.load_history()

    def setup_scrap(self) -> None:
        self.create_base_folders()
        self.create_files()

    def get_url(self, destination_path:str, index:int) -> str:
        self.destinations = read_json_file(destination_path)
        return self.destinations[index]
    
    def get_dest_count(self, destination_path:str) -> None:
        self.dest_count = len(read_json_file(destination_path))
        print(f"\t {self.dest_count} dest urls")

    def soupify_page(self) -> object:
        return BeautifulSoup(self.driver.page_source, 'lxml')
    
    def save_data(self) -> None:
        print("\t ===> saving ... ")
        if self.data_container:
            match(self.plateform):
                case 'maeva':
                    write_csv_file(self.output_file_path, constants.MAEVA_CSV_FIELDS, self.data_container)
    
    def api_save(self) -> None:
        pass

    @abstractmethod
    def data_is_valid(self) -> None:
        pass

    @abstractmethod
    def check_page(self) -> None:
        pass

    @abstractmethod
    def extract_data(self) -> None:
        pass






    
