from tkinter import messagebox
from datetime import datetime
from pathlib import Path
import pandas as pd
import json
import csv
import sys, os

def show_message(message_title:str, message_body:str,status:str) -> None:
    print(f"  ==> {message_body}")
    match status:
        case 'error':
            messagebox.showerror(message_title, message_body)
        case 'info':
            messagebox.showerror(message_title, message_body)
        case 'warning':
            messagebox.showwarning(message_title, message_body)

def report_bug(bug_file_path:str, bug:dict) -> None:
    if not Path(bug_file_path).exists():
        os.makedirs(bug_file_path)
    with open(bug_file_path, 'a') as bugfile:
        bug['datetime'] = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        bugfile.write(json.dumps(f"{bug}\n"))
    print(bug)

def load_json(json_file_path:str) -> object:
    try:
        return json.load(open(json_file_path))
    except:
        show_message('File not Found', "file does not exist or file path error", 'error')

def create_log_file(log_file_path:str, log_value:dict) -> None:
    if not Path(log_file_path).exists():
        with open(log_file_path, 'w') as log_file:
            log_file.write(json.dumps(log_value))

def save_history(log_file_path:str, log_value:dict) -> None:
    if Path(log_file_path).exists():
        with open(log_file_path, 'w') as log_file:
            log_file.write(json.dumps(log_value))
    else:
        show_message("History File Not Found", "log file history not found or may be deleted", "error")

def get_history(log_file_path:str, key:object) -> object | None:
    try:
        history = load_json(log_file_path)
        return history[key]
    except KeyError as e:
        print(e)

def create_file(file_path:str, field_names:list) -> None:
    if not Path(file_path).exists():
        with open(file_path, 'w') as file:
            writers = csv.writer(file)
            writers.writerow(field_names)

def save_data(file_path:str, data:list, field_names:str) -> None:
    with open(file_path, mode='a', newline='', encoding='utf-8') as outputfile:
        dict_writer_obect = csv.DictWriter(outputfile, fieldnames=field_names)
        dict_writer_obect.writerows(data)

