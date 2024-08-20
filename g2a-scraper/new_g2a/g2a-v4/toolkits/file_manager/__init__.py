import json
import csv
from pathlib import Path
import os
import aiofiles
from asgiref.sync import async_to_sync

@async_to_sync
async def async_read_json_file(json_file_path, key:str=None) -> object:
    try:
        async with await aiofiles.open(json_file_path) as openfile:
            content = await openfile.read()
            json_object = await json.loads(content)
            if key:
                return json_object[key]
            return json_object
    except FileNotFoundError:
        print("\t File not found")
        
def read_json_file(json_file_path, key:str=None) -> object:
    try:
        with open(json_file_path, 'r', encoding='utf-8') as openfile:
            json_object = json.load(openfile)
            if key:
                return json_object[key]
            return json_object
    except FileNotFoundError:
        print("\t File not found")

def write_json_file(json_file_path:str, value:object=None) -> None:
    try:
        with open(json_file_path, 'w', encoding='utf-8') as openfile:
            if value:
                openfile.write(json.dumps(value, indent=4))
    except FileNotFoundError:
        print("\t File not found!!!!")

def create_csv_file(file_path:str, field_names:list) -> None:
    if not Path(file_path).exists():
        with open(file_path, 'w', encoding='utf-8') as file:
            writers = csv.writer(file)
            writers.writerow(field_names)

def write_csv_file(file_path:str, field_names:list, data:list=[]) -> None:
    with open(file_path, mode='a', newline='', encoding='utf-8') as outputfile:
        dict_writer_obect = csv.DictWriter(outputfile, fieldnames=field_names)
        dict_writer_obect.writerows(data)

def resolve_folder_path(folder_path:str) -> None:
    if not Path(folder_path).exists():
        os.makedirs(folder_path)
