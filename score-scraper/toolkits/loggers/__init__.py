import logging
import os
import smtplib
from colorama import Fore
# from core import constants as ct


# logging.basicConfig(level=logging.INFO, format=Fore.YELLOW + '%(asctime)s - %(levelname)s - %(message)s')

def show_message(msg_type:str, message:str, hide_in_prod:bool=True) -> None:
    if hide_in_prod:
        return
    match msg_type.lower():
        case 'info':
            logging.info(Fore.GREEN + message)
        case 'debug':
            logging.debug(Fore.CYAN + message)
        case 'warnning':
            logging.warning(Fore.BLUE + message)
        case 'error':
            logging.error(Fore.RED + message)
        case 'critical':
            logging.critical(message)

def get_input(message:str) -> object:
    response = input(Fore.GREEN + f"$ {message} ==> ") 
    return response

def report_bug(data:object) -> None:
    pass

def get_log(plateform:str, week_date:str, file_name:str) -> object:
    pass

def report_status():
    pass