import os 
import csv
import json
from toolkits import loggers

from pathlib import Path


ct = ""

PLATEFORM = ['booking', 'maeva', 'edomizil', 'campings', 'yellohvillage']


def create_folder_if_not_exist(folder_path:str) -> None:
    """create folder if it doesn't exist yet
    Args:
        folder_path (Path): path of the directory
    """ 
    if not Path(folder_path).exists():
        os.makedirs(folder_path)
        loggers.show_message('info', f"folder path {folder_path} created")

def create_or_update_json_file(file_path:str, file_content:object=None) -> None:
    """create or update file content
    Args:
        file_path (Path): path to the file
        file_content (object): content to be add into the file
    """
    if not Path(file_path).exists():
        with open(file_path, 'w') as openfile:
            pass
    if file_content:
        with open(file_path, 'w') as openfile:
            openfile.write(json.dumps(file_content))
    loggers.show_message('info', "file data updated")

def get_json_file_content(json_file_path:str, key:str=None) -> object:
    """get json file content
    Args:
        json_file_path (str): json file path
    Returns:
        object: json file content
    """
    if Path(json_file_path).exists():
        with open(json_file_path, 'r') as openfile:
            file_content = json.load(openfile)
            if key:
                try:
                    return file_content[key]
                except KeyError as e:
                    loggers.show_message('error',f"{e}")
            return file_content
    loggers.show_message('error', 'file does not found')

def save_data_to_csv(file_path:str, data:list, field_names:str) -> None:
    """save data to csv file
    Args:
        file_path (str): csv file path
        data (list): list of data to be saved
        field_names (str): filed names of csv file
    """
    with open(file_path, mode='a', newline='', encoding='utf-8') as outputfile:
        dict_writer_object = csv.DictWriter(outputfile, fieldnames=field_names)
        dict_writer_object.writerows(data)

def save_data_to_json(file_path:str, data:object, key:str=None) -> None:
    """save data to a json file
    Args:
        file_path (str): json file path
        data (object): list of data to be saved
        key (str, optional): key of data type list to be updated or none in case that all data will be updated. Defaults to None.
    """
    file_content = get_json_file_content(file_path)
    if key:
        file_content[key] += [*data]
    create_or_update_json_file(file_path, file_content)

def check_plateform(plateform:str) -> None:
    global PLATEFORM
    if plateform.lower() not in PLATEFORM:
        loggers.show_message('error', 'plateform not reconized')

# def get_selectors(plateform:str) -> object:
#     check_plateform(plateform)
#     return get_json_file_content(f"{ct.APPS_FOLDER_PATH}/apps/{plateform}/selectors.json")
    
# def get_stations(plateform:str, key:str=None) -> object:
#     check_plateform(plateform)
#     if key:
#         return get_json_file_content(f"{ct.APPS_FOLDER_PATH}/configs/{plateform}/station.json", key)
#     return get_json_file_content(f"{ct.APPS_FOLDER_PATH}/configs/{plateform}/station.json")

def get_path(plateform:str, folder_name:str) -> str | None:
    check_plateform(plateform)
    match folder_name:
        case 'statics':
            return f"{ct.APPS_FOLDER_PATH}/statics/{plateform}/"
        case 'dests':
            return f"{ct.APPS_FOLDER_PATH}/dests/{plateform}/"
        case 'log':
            return f"{ct.LOGS_FOLDER_PATH}/{plateform}/"
        case 'output':
            return f"{ct.OUTPUT_FOLDER_PATH}/{plateform}/"
        