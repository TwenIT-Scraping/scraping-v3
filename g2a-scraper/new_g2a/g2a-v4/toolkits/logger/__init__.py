from colorama import Fore, just_fix_windows_console
from tkinter import messagebox
from pathlib import Path
from datetime import datetime
from prettytable import PrettyTable
import os, json
import platform
import pandas as pd

if platform.system().lower() == 'windows':
    just_fix_windows_console()


def show_message(message_title:str, message_body:str,status:str) -> None:
    print(f"\t  ==> {message_body}")
    match status:
        case 'error':
            messagebox.showerror(message_title, message_body)
            print(Fore.RED + f"\t {message_body}")
        case 'info':
            messagebox.showerror(message_title, message_body)
            print(Fore.BLUE + f"\t {message_body}")
        case 'warning':
            messagebox.showwarning(message_title, message_body)
            print(Fore.YELLOW + f"\t {message_body}")


def clear_logs() -> None:
    if platform.system().lower() == 'windows':
        os.system('cls')
    else:
        os.system('clear')

def show_datatable(data_source:list, field_names:list) -> None:
    table = PrettyTable(field_names)
    df = pd.DataFrame(data_source)
    df = df[field_names]
    for i in range(len(df)):
        item = df.iloc[i].to_dict()
        data_field = []
        for x in item.keys():
            if len(str(item[x])) > 12:
                data_field.append(str(item[x][0:12]) + "...")
            else:
                data_field.append(item[x])
        table.add_row(data_field)
    print(table)

def report_bug(bug_file_path:str, bug:str) -> None:
    with open(bug_file_path, 'a') as bugfile:
        bug = f"{bug} - {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}\n"
        bugfile.write(bug)
    print(Fore.RED + f"\t ===> {bug}")