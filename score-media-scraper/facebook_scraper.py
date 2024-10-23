from playwright.sync_api import sync_playwright
from random import randint
from bs4 import BeautifulSoup
import time
import json
import os
from datetime import datetime, timedelta
from dateutil import parser
from scraping import Scraping
from progress.bar import ChargingBar, FillingCirclesBar

__to_remove__ = ["j'aime", "followers", "likes", 'j’aime', 'suivi(e)s']


class FacebookProfileScraper(Scraping):

    def __init__(self, items: list = []) -> None:
        super().__init__(items)
        self.set_credentials('facebook')

        self.hotel_page_urls = []
        self.xhr_calls = []

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False, args=['--start-maximized'], channel='chrome')
        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()
        self.source = "facebook"

    def stop(self):
        self.context.close()

    def create_logfile(self, logfile_name: str) -> None:
        pass

    def load_history(self) -> None:
        pass

    def set_history(self, key: str, value: any) -> None:
        pass

    def resolve_loginform(self) -> None:
        self.fill_loginform()

    def goto_login(self) -> None:
        self.page.goto("https://www.facebook.com/")
        self.page.wait_for_timeout(randint(5000, 30000))

    def fill_loginform(self) -> None:
        try:
            time.sleep(5)
            self.page.wait_for_selector(
                "[id='email']", timeout=randint(5000, 30000))
            self.page.locator("[id='email']").click()
            time.sleep(.5)
            self.page.fill("[id='email']", self.current_credential['email'])
            time.sleep(.3)
            self.page.locator("[id='pass']").click()
            time.sleep(.2)
            self.page.fill("[id='pass']", self.current_credential['password'])
            time.sleep(.1)
            self.page.locator("[type='submit']").click()
            self.page.wait_for_timeout(randint(5000, 30000))
        except:
            print('tsy tafiditra')

    def goto_fb_page(self) -> None:
        #correction de certain url
        if 'https://www.facebook.com/https://www.facebook.com' in self.url:
            self.url = self.url.replace('https://www.facebook.com/https://www.facebook.com', 'https://www.facebook.com')
            
        self.page.goto(self.url, timeout=randint(30000, 80000))
        self.page.wait_for_timeout(randint(5000, 30000))
        time.sleep(.5)

    def format_values(self, data: object) -> int:
        pass

    def format_string_to_number(self, value: str) -> int | None:

        def digit_only(text):
            new_text = ""
            for t in text:
                if t.isdigit():
                    new_text += t
            return new_text

        text = value.lower()

        for t in __to_remove__:
            text = text.replace(t, '')

        print(text)

        try:

            if "k" in text:
                tmp = text.split(',')
                if len(tmp) > 1:
                    first = int(digit_only(tmp[0]))*1000
                    second = int(digit_only(tmp[1]))*100
                    return first+second

                else:
                    return int(digit_only(tmp[0]))*1000

            if "m" in text:
                tmp = text.split(',')
                if len(tmp) > 1:
                    first = int(digit_only(tmp[0]))*1000000
                    second = int(digit_only(tmp[1]))*100000
                    print(first, second, first+second)
                    return first + second
                else:
                    return int(digit_only(tmp[0]))*1000000

            else:
                return int(digit_only(text))

        except Exception as e:
            print(e)

        # numb = text.replace('K', "000").replace('k', "000").replace(
        #     'M', '000000').replace('.', '').replace(',', '')

        return 0

    def extract_data(self) -> None:
        try:
            soupe = BeautifulSoup(self.page.content(), 'lxml')
            
            # Récupération du nom de la page
            page_name_div = soupe.find('div', {'class': "x1e56ztr x1xmf6yo"})
            page_name = page_name_div.text if page_name_div else ''
            
            # Récupération du header
            header = soupe.find('div', {
                'class': 'x78zum5 x15sbx0n x5oxk1f x1jxijyj xym1h4x xuy2c7u x1ltux0g xc9uqle'
            })
            
            if header:
                h1_tag = header.find('h1', {
                    'class': 'html-h1 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1vvkbs x1heor9g x1qlqyl8 x1pd3egz x1a2a7pz'
                })
                page_name = h1_tag.text.replace('\xa0', '') if h1_tag else page_name
            
                # Récupération des likes et followers
                followers_likes = header.find_all(
                    'a', {'class': 'x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1sur9pj xkrqix3 xi81zsa x1s688f'}
                )

                if len(followers_likes) >= 2:
                    #page_likes = self.format_string_to_number(followers_likes[0].text)
                    #None car on n'a pas de données pour les likes
                    page_likes = None 
                    print("Page likes:", page_likes)
                    page_followers = self.format_string_to_number(followers_likes[0].text)
                    print("Page Followers: ", page_followers)
                else:
                    print("Followers and likes sections not found!")
                    self.add_logging("Followers and likes sections not found!")
                    self.errors = True
            else:
                print("Header not found!")
                self.add_logging("Header not found!")
                self.errors = True

            # Si pas d'erreurs, construire les données
            if not self.has_errors():
                self.page_data = {
                    'name': f"fb_{page_name}",
                    'likes': page_likes,
                    'followers': page_followers,
                    'source': 'facebook',
                    'establishment': f"/api/establishments/{self.establishment}",
                    'posts': 0
                }
                print(self.page_data)
            
        except Exception as e:
            print(f"An error occurred during data extraction: {e}")
            self.add_error(e)


    def execute(self) -> None:
        """progress = ChargingBar('Preparing ', max=3)
        
        # Étape 1: Initialiser les identifiants
        self.set_current_credential(0)
        progress.next()
        print(" | Open login page")
        
        # Étape 2: Ouvrir la page de connexion
        self.goto_login()
        progress.next()
        print(" | Fill login page")
        
        # Étape 3: Remplir le formulaire de connexion
        self.fill_loginform()
        progress.next()
        print(" | Logged in!")"""
        
        # Commencer à traiter les éléments
        progress = ChargingBar('Processing ', max=len(self.items))
        output_files = []
        
        for item in self.items:
            p_item = FillingCirclesBar(item['establishment_name'], max=4)
            
            try:
                # Étape 4: Définir l'élément courant
                self.set_item(item)
                self.add_logging(f"Open page: {item['establishment_name']}")
                p_item.next()
                print(f" | Open page: {item['establishment_name']}")
                
                # Étape 5: Ouvrir la page Facebook
                self.goto_fb_page()
                p_item.next()
                print(" | Extracting")
                
                # Étape 6: Extraire les données
                self.extract_data()
                self.add_logging(f"=> Data extracted for {item['establishment_name']}!")
                p_item.next()
                
                # Étape 7: Sauvegarder les données si aucune erreur
                if not self.has_errors():
                    print(" | Saving")
                    saved_file = self.save()
                    output_files.append(saved_file)
                    self.add_logging(f"=> Saved in local file: {saved_file}!")
                    p_item.next()
                    print(" | Saved")
                
                # Réinitialiser les erreurs pour l'élément suivant
                self.reset_error()

            except Exception as e:
                # Capturer et afficher l'erreur
                self.add_error(e)
                print(f"An error occurred while processing {item['establishment_name']}: {e}")
            
            progress.next()
        
        # Optionnel: Retourner les fichiers sauvegardés ou ajouter d'autres actions
        print(f"Processing completed. Files saved: {output_files}")


        self.stop()
        print(output_files)
        return output_files
