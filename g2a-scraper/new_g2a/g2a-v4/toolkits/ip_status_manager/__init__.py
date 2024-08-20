from toolkits.constants import PROJECT_FOLDER_PATH
from toolkits.file_manager import async_read_json_file, write_json_file, read_json_file
from asgiref.sync import async_to_sync
import asyncio



IP_STATUS_FILE = f"{PROJECT_FOLDER_PATH}/configs/ip_status.json"


# def get_status(key:str=None) -> dict:
#     global IP_STATUS_FILE
#     if key:
#         status = asyncio.run(async_read_json_file(IP_STATUS_FILE, key))
#         return satus
#     status = asyncio.run(async_read_json_file(IP_STATUS_FILE))
#     return status
    
def get_status(key:str=None) -> dict:
    global IP_STATUS_FILE
    if key:
        status = read_json_file(IP_STATUS_FILE, key)
        return status
    status = read_json_file(IP_STATUS_FILE)
    return status

def set_status(key:str, value:object) -> None:
    global IP_STATUS_FILE
    current_status = read_json_file(IP_STATUS_FILE)
    try:
        current_status[key] = value
        write_json_file(IP_STATUS_FILE, current_status)
    except:
        print("\t Cannot change IP status")
