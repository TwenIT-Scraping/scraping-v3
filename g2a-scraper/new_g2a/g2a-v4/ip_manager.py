import argparse
import subprocess
import platform
import time
import sys
import os
import shlex
from datetime import timedelta
from colorama import just_fix_windows_console, Fore
from toolkits.logger import show_message
from toolkits.ip_status_manager import set_status, get_status
from toolkits.constants import PROTONVPN_CONNEXION_ID, NORDVPN_CONNEXION_ID


CITIES = {
    'france': {'protonvpn':'fr', 'nordvpn':'fr854'},
    'suisse': {'protonvpn':'ch', 'nordvpn':'ch408'},
    'spain': {'protonvpn':'es', 'nordvpn':''}
}


ORIGIN = ['prontonvpn', 'nordvpn']


if platform.system().lower() == 'windows':
    just_fix_windows_console()

class IP_Timer(object):

    def __init__(self, city:str, origin:str, countdown:int=5, time_type:str='min') -> None:
        self.countdown = countdown
        self.time_type = time_type
        self.origin = origin
        self.city = city.lower()
        self.time_types = ['s', 'm', 'h']
        self.countdown_time = 0

    def set_origin(self, new_origin:str) -> None:
        global ORIGIN
        if new_origin in ORIGIN:
            self.origin = new_origin
        else:
            print(f"\t ==> provider {new_origin} not registered")

    def set_city(self, new_city:str) -> None:
        global CITIES
        if new_city in CITIES.keys():
            self.city = new_city
        else:
            print(f"\t ==> city {new_city} not registered")

    def params_is_valide(self) -> bool:
        if self.time_type not in self.time_types:
            return False
        if self.countdown < 0:
            return False
        if self.city not in CITIES.keys():
            print(f"\t    uncreconized value for city. value should be one of {CITIES.keys()}")
            return False
        if self.origin not in ['protonvpn', 'nordvpn']:
            print(f"\t    uncreconized value for origin. value should be protonvpn or nordvpn")
            return False
        return True
    
    def get_command(self) -> object:
        global CITIES
        match(self.origin):
            case 'protonvpn':
                    activation_command = f"sudo nmcli conn up {CITIES[self.city]['protonvpn']}.{PROTONVPN_CONNEXION_ID}"
                    desactivation_command = f"sudo nmcli conn down {CITIES[self.city]['protonvpn']}.{PROTONVPN_CONNEXION_ID}"
                    return activation_command, desactivation_command
            case 'nordvpn':
                    activation_command = f"sudo nmcli conn up {CITIES[self.city]['nordvpn']}.{NORDVPN_CONNEXION_ID}"
                    desactivation_command = f"sudo nmcli conn down {CITIES[self.city]['nordvpn']}.{NORDVPN_CONNEXION_ID}"
    
    def get_time_type(self) -> str:
        if self.params_is_valide():
            return self.time_type

    def normalize_time(self) -> None:
        if self.params_is_valide():
            match(self.time_type):
                case 's':
                    self.countdown_time = self.countdown
                case 'm':
                    self.countdown_time =  timedelta(minutes=self.countdown).total_seconds()
                case 'h':
                    self.countdown_time = timedelta(hours=self.countdown).total_seconds()
        else:
            show_message('time type error', f"time type should be one of {self.time_types} \n and countdown must be positive integer", 'error')
            time.sleep(2)
            sys.exit()

    def show_time(self, timerest:int) -> None:
        color = Fore.RED if timerest <= 60 else Fore.GREEN
        print(Fore.GREEN + " $ time left before IP will be changed " + color + time.strftime("%H:%M:%S", time.gmtime(timedelta(seconds=timerest).total_seconds())), end='\r')
        self.time_rest -= 1
        time.sleep(1)

    def reset_time(self) -> None:
        self.time_rest = self.countdown_time

    def force_ip_rotation(self, city:str='france', origin:str='protonvpn') -> None:
        global CITIES
        global ORIGIN
        if city.lower() in CITIES.keys() and origin.lower() in ORIGIN:
            self.set_city(city)
            self.set_origin(origin)
            self.launch_command()
            pass
        else:
            print(f"\t ==> city {city} not registered")

    def launch_command(self) -> None:
        activation_cmd, desactivation_cmd = self.get_command()
        if platform.system().lower() == 'windows':
            print("\n\t It's time to change IP, please do It then press enter")
        else:
            print('\n\t desctivation ... ')
            print("\t " + desactivation_cmd)
            try:
                print(f"\t ===> connexion status: {get_status()}")
                subprocess.run(shlex.split(desactivation_cmd), check=True)
                set_status(key='STATUS', value='desactivated')
                set_status(key='ORIGIN', value=self.origin)
                set_status(key='CITY', value=self.city)
            except subprocess.CalledProcessError as e:
                print(f"\t ===> error {e}")
            print('\t activation ... ')
            print("\t " + activation_cmd)
            time.sleep(.5)
            try:
                print(f"\t ==> connexion status: {get_status()}")
                subprocess.run(shlex.split(activation_cmd), check=True)
                set_status(key='STATUS', value='activated')
                set_status(key='ORIGIN', value=self.origin)
                set_status(key='CITY', value=self.city)
            except subprocess.CalledProcessError as e:
                print(f"\t ===> error {e}")

    def run(self) -> None:
        print(" $ starting ... ")
        time.sleep(1)
        self.normalize_time()
        try: 
            while True:
                self.reset_time()
                while self.time_rest >= 0:
                    self.show_time(self.time_rest)
                self.launch_command()
        except KeyboardInterrupt:
            print('\t stopping ...')


def main_arguments() -> object:
    parser = argparse.ArgumentParser(description="IP manager program", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--action', '-a', dest='action', default='',help="")
    parser.add_argument('--duration', '-d', dest='duration', default='5', help="time cycle duration for each new IP")
    parser.add_argument('--unit', '-u', dest='unit', default='s', help="unit of time [s for second m for minute and h for hour]")
    parser.add_argument('--origin', '-o', dest='origin', default='protonvpn', help="connexion origin protonvpn vpn or nordvpn")
    parser.add_argument('--city', '-c', dest='city', default='c', help="city where you wish the origin of IP")
    return parser.parse_args()


ARGS_INFO = {
        '-a': {'long': '--action', 'dest': 'action', 'help': "action to be performed"},
        '-d': {'long': '--duration', 'dest': 'duration', "help": "time cycle duration for each IP"},
        '-u': {'long': '--unit', 'dest': 'unit', "help": "time unit [s for second m for minute and h for hour]"},
        '-o': {'long': '--origin', 'dest': 'origin', "help": "connexion origin protonvpn vpn or nordvpn"},
        '-c': {'long': '--city', 'dest': 'city', "help": "city where you wish the origin of IP"},
    }

def check_arguments(args, required):
    miss = []

    for item in required:
        if not getattr(args, ARGS_INFO[item]['dest']):
            miss.append(f'{item} ou {ARGS_INFO[item]["long"]} ({ARGS_INFO[item]["help"]})')

    return miss

if __name__ == '__main__':
    args = main_arguments()

    if args.action and args.action == 'start':
        miss_command = check_arguments(args, ['-a', '-d', '-u', '-c', '-o'])
        if len(miss_command):
            raise Exception(f"Argument(s) manquant(s): {', '.join(miss_command)}")
        else:
            ip_manager = IP_Timer(
                countdown=int(args.duration),
                time_type=args.unit,
                city=args.city,
                origin=args.origin
            )
            ip_manager.run()