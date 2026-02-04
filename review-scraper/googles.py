import os
import random
import pandas as pd
from scraping import Scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.common.keys import Keys
from lingua import Language, LanguageDetectorBuilder
from changeip import refresh_connection

from selenium.webdriver.common.action_chains import ActionChains


def format_date_fr(date_str:str) -> str:
    month_fr = {
    "janvier": "01",  
    "février": "02",  
    "mars": "03",  
    "avril": "04",  
    "mai": "05",  
    "juin": "06",  
    "juillet": "07",  
    "août": "08",  
    "septembre": "09",  
    "octobre": "10",  
    "novembre": "11",  
    "décembre": "12" 
    }
    #04 02 2026 ajout check car parfois erreur dedans je ne sais pas encore pourquoi
    try:
        date_str = date_str.lower().replace('visité en ', '')
        print(f'date visite fr => {date_str}')
        if len(date_str.split(' ')) == 1:
            print(f'date visite fr mois seul => {date_str}')
            return f"{datetime.now().day}/{month_fr[date_str]}/{datetime.now().year}"
        if len(date_str.split(' ')) == 2 and int(date_str.split(' ')[-1]) > 31:
            print(f'date visite fr mois et année => {date_str}')
            return f"{datetime.now().day}/{month_fr[date_str]}/{int(date_str.split(' ')[-1])}"
    except Exception as e:
        input(f'erreur dans format date fr => {e}')

all_language = ['en','de','fe','es']
class BaseGoogleScrap(Scraping):
    def __init__(self, 
                 url: str, 
                 establishment: str, 
                 settings: str, 
                last_review_date:str,
                 env: str):
        super().__init__(in_background=False, url=url,
                         establishment=establishment, 
                         settings=settings, 
                        last_review_date=last_review_date,
                         env=env) 
        self.url_lang_code = {
            'fr': 'fr-FR',
            'en': 'en-EN',
            'es': 'es-ES',
        }
        self.data_loaded = False
        self.data = []

        self.number_retry = 0

    def detect_lang(self, text: str) -> str:
        if text:
            lang_code = {
                'Language.ENGLISH': 'en',
                'Language.GERMAN': 'de',
                'Language.SPANISH': 'es',
                'Language.FRENCH': 'fr',
            }

        languages = [Language.ENGLISH, Language.FRENCH,
                     Language.GERMAN, Language.SPANISH]
        detector = LanguageDetectorBuilder.from_languages(*languages).build()
        try:
            return lang_code[f"{detector.detect_language_of(text)}"]
        except:
            return ''

    def is_handball(self) -> bool:
        return True if '&topic=mid:/' in self.driver.current_url else False
    
    def is_travel(self) -> bool:
        return True if '/travel/' in self.driver.current_url else False


    def load_reviews(self) -> None:
        if not self.is_travel():
             #16 12 2025 : nouvel afficahge encore apparu le 03 12 2025, test finalement achevé le 16 12 2025 , à suivre de près car la page est très dynamique en terme de structure html
            try:
                time.sleep(random.uniform(0.8,0.9))
                exist = self.driver.find_element(By.CSS_SELECTOR, 'a[class="vwVdIc wzN8Ac rllt__link a-no-hover-decoration"]')
                # exist = exists[0].find_elements(By.CSS_SELECTOR,'a')
                #/html/body/div[3]/div/div[12]/div[1]/div[2]/div[2]/div/div/div[1]/div/div[3]/div/div[2]/div/div/div/a
                # input(f'msy ve => {exist}')
                if exist:
                    print('click on link establishment avant de retrouver une view normal')
                    # self.driver.execute_script("arguments[0].click();", exist)
                    self.driver.execute_script("""
                                            const el = arguments[0];
                                            const r = el.getBoundingClientRect();
                                            const cx = r.left + r.width/2;
                                            const cy = r.top + r.height/2;

                                            document.dispatchEvent(new MouseEvent('mousemove', {clientX: cx-30, clientY: cy-30, bubbles:true}));
                                            document.dispatchEvent(new MouseEvent('mousemove', {clientX: cx, clientY: cy, bubbles:true}));

                                            el.dispatchEvent(new MouseEvent('mousedown', {clientX: cx, clientY: cy, bubbles:true}));
                                            el.dispatchEvent(new MouseEvent('mouseup', {clientX: cx, clientY: cy, bubbles:true}));
                                            el.dispatchEvent(new MouseEvent('click', {clientX: cx, clientY: cy, bubbles:true}));
                                            """, exist)
                    time.sleep(random.uniform(0.5,1.2))
                    print('clicked')
                else:
                    input('élément à cliquer non trouvable, check selecteur')
            except Exception as e:
                # input(f'{e} -> pas de nouveau affichage detecté le 03 12 2025')
                print('pas de structure de page complexe')
                pass
            
            #20 11 2025 : nouvelle affichage google pour certains, clique sur popup avis
            try:
                time.sleep(random.uniform(0.8,0.9))
                exist= self.driver.find_elements(By.CSS_SELECTOR, '#rcnt > div:nth-child(3) > div > div > div > div > div.HdbW6.MjUjnf.VM6qJ.Mefd0c > div.hHq9Z.m0pBqd > div')
                if exist:
                    print('new')
                    check_view = 'new'
                else:
                    print('old')
                    check_view = 'old'
            except:
                pass

            if check_view == 'new':
                #clique sur AVIS en serveur seulement:
                try:
                    print('Nouvel affichage de google')
                    print('click popup avis')
                    try:
                        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="rcnt"]/div[2]/div/div/div/div/div[3]/div[1]/div/div/div[2]/div[2]/div[1]/div/span[3]/span/a')))
                        popup_avis = self.driver.find_element(By.XPATH, '//*[@id="rcnt"]/div[2]/div/div/div/div/div[3]/div[1]/div/div/div[2]/div[2]/div[1]/div/span[3]/span/a')
                    except:
                        #21 11 2025: Comte de CHalle other view
                        print('other selector for popup avis for new view BUT go to >>> old view <<<< ')
                        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="kp-wp-tab-overview"]/div[2]/div/div/div/div[2]/div/div/div/div/div/div[2]/a')))
                        popup_avis = self.driver.find_element(By.XPATH, '//*[@id="kp-wp-tab-overview"]/div[2]/div/div/div/div[2]/div/div/div/div/div/div[2]/a')
                        check_view = 'old' #pour la suite du code

                        #for Comte de Challe 26 11 2025
                        if "travel" in self.driver.current_url:
                            print('GOOGLE TRAVEL DETECTé, on passe à la suite')
                            return

                    time.sleep(random.uniform(0.5,1.2))
                    if popup_avis:
                        print('popup avis found')
                        # print(f'popup avis found => {popup_avis.text}')
                        self.driver.execute_script("arguments[0].click();", popup_avis)
                        print('popup avis clicked')

                    time.sleep(random.uniform(1.5,2.5)) #moins de 1 ça ne suffit pas
                except Exception as e:
                    input(f'popup avis click error => {e}')
                #end 20 11 2025
            else:
                try:
                    print('click tab avis')
                    WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="akp_tsuid_VgSRZ6DQLZqo0-kPreOHaQ_15"]/div/div[1]/div/g-sticky-content-container/div/block-component/div/div[1]/div/div/div/div[1]/div/div/div[5]/div[1]/g-sticky-content/div/div[1]/g-tabs/div/div/a[3]')))
                    avis = self.driver.find_elements(By.XPATH, '//*[@id="akp_tsuid_VgSRZ6DQLZqo0-kPreOHaQ_15"]/div/div[1]/div/g-sticky-content-container/div/block-component/div/div[1]/div/div/div/div[1]/div/div/div[5]/div[1]/g-sticky-content/div/div[1]/g-tabs/div/div/a[3]')
                    self.driver.execute_script("arguments[0].click();", avis)
                    time.sleep(1)
                    print('tab avis clicked')
                except Exception as e:
                    try:
                        #MAJ 21 11 2025 : nouveau selecteur pour tab avis car les affichages aussi changent avec d'autres etablissements
                        print('tab avis not clicked')
                        print('             ')
                        print('other selector for tab avis')
                        selector_tab_in_local = 'a[jsname="AznF2e"]'
                        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector_tab_in_local)))
                        avis_content = self.driver.find_elements(By.CSS_SELECTOR, selector_tab_in_local)[-1]
                        # input('avis found ')
                        self.driver.execute_script("arguments[0].click();", avis_content)
                        time.sleep(1)
                        print('tab avis clicked')
                    except Exception as e:
                        pass
                    pass
                #end 20 11 2025
            
            order_item = self.driver.find_elements(By.XPATH, "//div[@jsname='XPtOyb']")[1]
            self.driver.execute_script("arguments[0].click();", order_item)
            time.sleep(1)
            #20 02 2025
        else:
            try:
                time.sleep(2)
                self.driver.find_element(
                    By.XPATH, f"//button[@jsname='b3VHJd']").click()
                print("         ")
                print("Select ... ") #pour visibilité, je ne sais pas ce que c'est 04 02 2026
                print("         ") 

            except:
                pass
            try:
                self.driver.execute_script("window.scrollTo(0, 500);")
                order_dropdown = self.driver.find_element(
                    By.XPATH, "//div[@jsname='wQNmvb']")
                self.driver.execute_script(
                    "arguments[0].click();", order_dropdown)
                
                print("         ")
                print("Select container order review") #pour visibilité 04 02 2026
                print("         ")

                time.sleep(2)
                order_item = self.driver.find_elements(
                    By.XPATH, "//div[@jsname='V68bde']/div[@jsname='wQNmvb']")[1]
                self.driver.execute_script("arguments[0].click();", order_item)
                time.sleep(1)

                print("         ")
                print("Select view RECENT review OK") #pour visibilité 04 02 2026
                print("         ")

            except:
                print("pass review order (REVIEW DANS l'ORDRE PAR DEFAUT)...") #code origine, ce qui veut dire que si erreur le programme laisse passer, c'était le code d'origine , je laisse là
                pass

            try:
                self.driver.find_elements(By.XPATH, '//div[@jsname="XPtOyb"]')[1].click()
            except:
                pass

        index = 0
        scrollHeight = 500
        currentHeight = 0
        self.data_current_count = len(self.data)
        time.sleep(random.randint(1, 3))
        scroll_by_body = False

        #26 01 2026 : pour bien prendre en compte les view de google NON TRAVEL
        if not self.is_travel() and check_view == "old":
            try:
                center_element = self.driver.find_element(By.XPATH, '//div[@class="kp-header"]')
                if center_element:
                    print('element found')
                    center_element.click()
                    scroll_by_body = True
                print('old view google OK') #20 11 2025
                print('             ')
            except:
                pass
        elif not self.is_travel() and check_view == "new":
            try:
                print('new view google') #20 11 2025
                print('             ')
                center_element = self.driver.find_element(By.XPATH, '//*[@id="sZmt3b"]/div[2]/div[2]/c-wiz/div[3]/div/div[5]/div')
                if center_element:
                    print('element found')
                    center_element.click()
                    scroll_by_body = True
            except:
                input('aucun element trouvé, check le navigateur car sinon le scroll ne marchera pas')
                pass

        while not self.data_loaded:
            if scroll_by_body:
                for i in range(4):
                    self.driver.find_element(
                    By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            else:
                self.driver.execute_script(
                f"window.scrollTo({currentHeight}, {scrollHeight});")
            time.sleep(random.randint(1, 3))
            if index == 20:
                self.click_for_complete_review()
                self.driver.find_element(
                    By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)
                self.extract()
                self.save_data()

                #28 01 2026 : POUR CEUX DONT LA PAGE MMONTRE UN BUTTON "Autres avis d'utilisateurs" (rencontrés sur le nouvel établissement Zoo de La Flèche)
                try:
                    more_review_button = self.driver.find_elements(By.CLASS_NAME, 'Ji6mjb')
                    # input(f'exist more view button => {bool(more_review_button)}')
                    if more_review_button:
                        print('bouton autres avis utilisateurs trouvé')
                        ActionChains(self.driver, 1).move_to_element(more_review_button[0]).perform()
                        print('scroll to button more view')
                        self.driver.execute_script("arguments[0].click();", more_review_button[0])
                        print('bouton cliqué')
                        time.sleep(random.randint(2,4))
                except Exception as e:
                    print(f'erreur click autres avis utilisateurs => {e}')
                    input('Check navigateur pour voir si le bouton est là')
                    pass
                #fin 28 01 2026

                self.new_data_count = len(self.data)
                if self.new_data_count == self.data_current_count:
                    break
                self.data_current_count = self.new_data_count
                index = 0

            # else:
            #     for i in range(3):
            #         print('scrolling')
            #         self.driver.find_element(
            #             By.XPATH, '//div[@jsaction="WFrRFb;keydown:uYT2Vb"]').send_keys(Keys.PAGE_DOWN)
            #     if index == 10:
            #         self.extract()
            #         self.save_data()
            #         self.new_data_count = len(self.data)
            #         index = 0
            #         if self.new_data_count == self.data_current_count:
            #             print('breaked')
            #             break
            #         self.data_current_count = self.new_data_count

            index += 1
            currentHeight = scrollHeight
            scrollHeight += 200

    def format_url(self, language: str) -> str:
        try:
            hl_params_index = self.url.index('&hl=') + 4
            new_url = self.url[:hl_params_index] + \
                self.url_lang_code[language] + self.url[hl_params_index + 5:]
            print(new_url)
            return new_url
        except ValueError:
            print(f"{self.url}&hl={self.url_lang_code[language]}")
            return f"{self.url}&hl={self.url_lang_code[language]}"
        
    def click_for_complete_review(self):
        #MAJ 20 02 2025
        try:
            if not self.is_travel():
                plus_bouton = self.driver.find_elements(By.CSS_SELECTOR, 'a[class="MtCSLb"]')
                print(f'Sur cette section de page, il y a {len(plus_bouton)} review(s) non affiché complètement')
                script = "var buttons = document.querySelectorAll('a.MtCSLb');buttons.forEach(function(button) {button.click();}); "
                self.driver.execute_script(script)
                print('Tous les reviews doivent maintenant être affiché complètement')
                time.sleep(random.randint(2,3))
            else:
                en_savoir_plus_bouton = self.driver.find_elements(By.CSS_SELECTOR, 'span[jsname="kDNJsb"]')
                print(f'Sur cette section de page, il y a {len(en_savoir_plus_bouton)} review(s) non affiché complètement')
                #Npuvel méthode 04 02 2026, l'ancien proviquait des erreurs de DOM dynamique parfois
                self.driver.execute_script("""
                                            document
                                            .querySelectorAll('span[jsname="kDNJsb"]')
                                            .forEach(e => e.click());
                                            """)
                print('Tous les reviews doivent maintenant être affiché complètement')
                time.sleep(random.randint(2,3))
        except Exception as e:
            input(f"erreur => {e}")

    def execute(self) -> None:
        try:

            if self.force_refresh:
                refresh_connection()
            url = self.format_url(self.lang)
            self.set_url(url)
            #21 11 2025 : sauter LA PLAGE car travel
            if "PLAGE" in self.url:
                print("url de LA PAGE , pas de données, on saute")
                return
            #end 21 11 2025
            self.scrap()
            try:
                time.sleep(3)
                accept_btn = self.driver.find_element(
                    By.XPATH, "//span[contains(text(), 'Tout accepter') or contains(text(), 'Accept all')], or contains(text(), 'Aceptar todo')")
                self.driver.execute_script("arguments[0].click();", accept_btn)
                time.sleep(random.randint(2, 5))
            except:
                pass
            try:
                #accept_btn for google not travel
                time.sleep(3)
                accept_btn = self.driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button/span[6]')
                self.driver.execute_script("arguments[0].click();", accept_btn)
                time.sleep(random.randint(2, 5))
            except:
                pass
            time.sleep(5)
            WebDriverWait(self.driver, 10)
            if self.check_page():
                self.load_reviews()
                time.sleep(2)
                self.save()
            else:
                print("!!!!!!!! Cette page n'existe pas !!!!!!!!")
            self.driver.quit()
        except Exception as e:
            #MAJ 19 11 2025
                print('error execution')
                print("Check le naviguateru car il se peut que la page ne se soit pas chargé, actualissation et on reste")
                try:
                    if self.number_retry < 1:
                        self.number_retry += 1
                        self.execute()
                    else:
                        print('Trop de tentative échouée, on passe au prochain établissement')
                        pass
                except Exception as e:
                    print('3nd error execution - On passe au prochain établissement')
                    print(e)
                    pass

                    #code avant 22 09 2025 - ça bloque la continuation des autres provider
                    # self.driver.quit()
                    # sys.exit("Arret"

    def detect_date_lang(self, date:str) -> str:
        if date in ['minute','minutes','heure','heures','jour', 'jours', 'semaine', 'semaines', 'mois', 'an', 'ans']:
            return 'fr'
        elif date in ['minute','minutes','hour','hours','days', 'week', 'weeks', 'month', 'months', 'year', 'years']:
            return 'en'
        elif date in ['minuto','minutos','hora','horas','día', 'días', 'semana', 'semanas', 'mes', 'año', 'año']:
            return 'es'
        return ''
        #ajout heure dans la liste 02 07 2025 car ça n'a pas pris en compte les journaliers
        #ajout minute dans la liste 07 08 2025 


    def formate_date(self, raw_date: str) -> str:
        split_date = raw_date.split(' ')
        # print(split_date)
        #formattage des dates où il y a inscrit "modifié" [02 07 2025]
        if "modifié" in split_date[0]:
            # input(f'Commentaire ou Note modifié il y a {split_date[1]} {split_date[2]}')
            raw_date = raw_date.replace('modifié ','')
            split_date = raw_date.split(' ')
            # input(f'new split date sans modifié => {split_date}')
        today = datetime.now()
        language = self.detect_date_lang(split_date[1])
        match language:
            case "fr":
                if split_date[1] == 'jour':
                    return datetime.strftime(today + timedelta(days=-1), '%d/%m/%Y')
                elif split_date[1] == 'jours':
                    return datetime.strftime(today + timedelta(days=-(int(split_date[0]))), '%d/%m/%Y')
                if split_date[1] == 'semaine':
                    return datetime.strftime(today + timedelta(days=-7), '%d/%m/%Y')
                elif split_date[1] == 'semaines':
                    return datetime.strftime(today + timedelta(days=-7*int(split_date[0])), '%d/%m/%Y')
                elif split_date[1] == 'mois':
                    if split_date[0] == 'un':
                        return datetime.strftime(today + timedelta(days=-31), '%d/%m/%Y')
                    else:
                        return datetime.strftime(today + timedelta(days=-31*int(split_date[0])), '%d/%m/%Y')
                elif split_date[1] == 'an':
                    return datetime.strftime(today + timedelta(days=-365), '%d/%m/%Y')
                elif split_date[1] == 'ans':
                    return datetime.strftime(today + timedelta(days=-(int(split_date[0])*365)), '%d/%m/%Y')
                else:
                    return datetime.strftime(today, '%d/%m/%Y')

            case"en":
                if split_date[1] == 'days':
                    return datetime.strftime(today + timedelta(days=-(int(split_date[0]))), '%d/%m/%Y')
                if split_date[1] == 'week':
                    return datetime.strftime(today + timedelta(days=-7), '%d/%m/%Y')
                elif split_date[1] == 'weeks':
                    return datetime.strftime(today + timedelta(days=-7*int(split_date[0])), '%d/%m/%Y')
                elif split_date[1] == 'months' or split_date[1] == 'month':
                    if split_date[0] == 'a':
                        return datetime.strftime(today + timedelta(days=-31), '%d/%m/%Y')
                    else:
                        return datetime.strftime(today + timedelta(days=-31*int(split_date[0])), '%d/%m/%Y')
                elif split_date[1] == 'year':
                    return datetime.strftime(today + timedelta(days=-365), '%d/%m/%Y')
                elif split_date[1] == 'years':
                    return datetime.strftime(today + timedelta(days=-(int(split_date[0])*365)), '%d/%m/%Y')
                else:
                    return datetime.strftime(today, '%d/%m/%Y')
            case "es":
                if split_date[1] == 'día':
                    return datetime.strftime(today + timedelta(days=-1), '%d/%m/%Y')
                if split_date[1] == 'días':
                    return datetime.strftime(today + timedelta(days=-(int(split_date[0]))), '%d/%m/%Y')
                if split_date[1] == 'semana':
                    return datetime.strftime(today + timedelta(days=-7), '%d/%m/%Y')
                elif split_date[1] == 'semanas':
                    return datetime.strftime(today + timedelta(days=-7*int(split_date[0])), '%d/%m/%Y')
                elif split_date[1] == 'mes' or split_date[1] == 'meses':
                    if split_date[0] == 'un':
                        return datetime.strftime(today + timedelta(days=-31), '%d/%m/%Y')
                    else:
                        return datetime.strftime(today + timedelta(days=-31*int(split_date[0])), '%d/%m/%Y')
                elif split_date[1] == 'año':
                    return datetime.strftime(today + timedelta(days=-365), '%d/%m/%Y')
                elif split_date[1] == 'años':
                    return datetime.strftime(today + timedelta(days=-(int(split_date[0])*365)), '%d/%m/%Y')
                else:
                    return datetime.strftime(today, '%d/%m/%Y')

    def save_data(self) -> None:
        new_data = []
        df = pd.DataFrame(self.data)
        df.drop_duplicates(subset=['rating', 'author', 'date_review', 'comment',
                           'language', 'source', 'date_visit', 'novisitday'], inplace=True)
        for i in range(len(df)):
            new_data.append(df.iloc[i].to_dict())
        self.data = new_data
        print(f"New data not in database ready to post => {self.data}")
        print("=>  Actual datas to post: ", len(self.data))


class Google(BaseGoogleScrap):

    def __init__(self, url: str, 
                 establishment: str, 
                 settings: str,
                 last_review_date: str,  
                 env: str):
        super().__init__(
            url=url, 
            establishment=establishment, 
            settings=settings,
            last_review_date=last_review_date, 
            env=env)

        # self.chrome_options.add_argument(f'--lang={self.lang}')
        # self.chrome_options.add_argument('--disable-translate')
        self.data_loaded = False
        # self.driver = webdriver.Chrome(options=self.chrome_options)

        self.driver.maximize_window()

    def extract(self) -> list:
        print('extraction..')
        reviews = []

        try:
            self.driver.find_element(
                By.XPATH, "//div[@role='listbox' and @jsname='fMAOF']").click()
            time.sleep(random.uniform(.5, 2.5))
            self.driver.find_element(
                By.XPATH, "//div[@role='option' and @data-value='2' and @data-hveid='CAMQkAY']").click()
            time.sleep(random.uniform(.2, 2))
        except:
            pass

        #load comments for non google travel page (déja réglé avec la fonction click for complete review)
        # try:
        #     view_more_btns = self.driver.find_elements(By.XPATH, "//a[@jsaction='KoToPc']")
        #     for view_more_btn in view_more_btns:
        #         view_more_btn.location_once_scrolled_into_view
        #         view_more_btn.click()
        # except:
        #     pass

        page = self.driver.page_source

        try:
            soupe = BeautifulSoup(page, 'lxml')
            container = ''
            cards = []
            if self.is_handball():
                container = soupe.find('div', {'class': 'aSzfg'})
                cards = container.find_all('div', {'class': 'bwb7ce'})
                print(f"{len(cards)} handball cards found")
            elif self.is_travel():
                container = soupe.find('div', {'jsname':'SvNErb'})
                cards = container.find_all('div', {'class':'Svr5cf bKhjM'})
                print(f"{len(cards)} google travel cards found")
            else:
                try:
                    container = soupe.find('div', {'jsname': 'SvNErb'})
                    cards = container.find_all('div', {'class': 'Svr5cf bKhjM'})
                    print(f"{len(cards)} simple google cards found")
                except:
                    cards = soupe.find_all('div', {'jsname':'ShBeI'})
                    print(f"{len(cards)} simple google cards found")

            for card in cards:

                author = ''
                comment = ''
                date_raw = ''
                rating = 0
                date_review = ''
                date_visit = ''
                lang = ''
                url = self.driver.current_url

                if self.is_travel():
                    #code comment before 20 02 2025
                    # if 'google' in card.find('span', {'class':'iUtr1 CQYfx'}).text.lower():
                    #     author = card.find('a', {'class':'DHIhE QB2Jof'}).text.strip() if card.find('a', {'class':'DHIhE QB2Jof'}) else ""
                    #     try:
                    #         comment = ""
                    #         if card.find('div', {'jsname':'NwoMSd'}):
                    #             comment = card.find('div', {'jsname':'NwoMSd'}).find('span').text
                    #         else:
                    #             comment = card.find('div', {'class':'K7oBsc'}).find('span').text if card.find('div', {'class':'K7oBsc'}) else ""
                    #         comment = comment.replace('(Traducido por Google) ', '').replace('\xa0... Ver más', '').replace(" En savoir plus", "") \
                    #         .replace('(Traduit par Google)', '').replace('(Translated by Google)', '').replace('(Original)', '')
                    #         try:
                    #             if comment and "avis d'origine" in comment.lower():
                    #                 comment = comment.lower().split("(avis d'origine)")[-1]
                    #             if comment and "(original)" in comment:
                    #                 comment = comment.lower().split("(original)")[-1]
                    #         except:
                    #             pass
                    #         try:
                    #             lang = self.detect_lang(comment)
                    #         except:
                    #             lang = self.lang
                    #         try:
                    #             date_visit_content = card.find('div', {'class':'DmVtKb'}).text.strip()
                    #         except:
                    #             date_visit_content = ""

                    #         match lang:
                    #             case 'fr':
                    #                 date_visit = format_date_fr(date_visit_content) if date_visit_content else ""
                    #     except:
                    #         comment = ""
                        
                    #     url = self.driver.current_url

                    #     rating = card.find('div', {'class': 'GDWaad'}).text.strip() if card.find('div', {'class': 'GDWaad'}) else rating
                    #     date_raw = card.find('span', {'class': 'iUtr1 CQYfx'}).text.lower()

                    #     if 'sur' in date_raw:
                    #         date_raw = date_raw[:date_raw.index(' sur')]
                    #     if 'on' in date_raw:
                    #         date_raw = date_raw[:date_raw.index(' on')]
                    #     if 'en' in date_raw:
                    #         date_raw = date_raw[:date_raw.index(' en')]

                    #     date_raw = date_raw.replace('il y a ', '').replace('\xa0', ' ').replace('hace ', '').replace('ago', '')
                    # else:
                    #     print('other site')
                    #     continue
                    if 'google' in card.find('span', {'class':'iUtr1 CQYfx'}).text.lower():
                        author = card.find('a', {'class':'DHIhE QB2Jof'}).text.strip() if card.find('a', {'class':'DHIhE QB2Jof'}) else ""
                        #20 02 2025 code
                        try:
                            comment = ""
                            if card.find('div', {'jsname':'NwoMSd'}):
                                # selecteur span avec tous les reviews même sans cliqué (vérifié le 20 02 2025)
                                comment = card.find('div', {'jsname':'NwoMSd'}).find('span').text
                            elif card.find('div', {'class':'K7oBsc'}):
                                try:
                                    comment = card.find('div', {'class':'K7oBsc'}).find('span').text
                                except:
                                    pass
                            else:
                                #ce bloc pour les auteurs ne laissant pas de commentaire
                                comment = ""
                            if comment == "":
                                pass
                            else:
                                comment = comment.replace('(Traducido por Google) ', '').replace('\xa0... Ver más', '').replace(" En savoir plus", "") \
                                .replace('(Traduit par Google)', '').replace('(Translated by Google)', '')
                                print("                     ")
                                comment_view_in_page = comment
                                if "avis d'origine" in comment.lower():
                                    two_comment = True
                                    comment_original_language = comment.lower().split("(avis d'origine)")[-1]
                                    comment_traduct = comment.lower().split("(avis d'origine)")[0]
                                elif "(original)" in comment.lower():
                                    two_comment = True
                                    comment_original_language = comment.lower().split("(original)")[-1]
                                    comment_traduct = comment.lower().split("(original)")[0]
                                else:
                                    two_comment = False

                                if two_comment:
                                    # print("                     ")
                                    # print('Two comments, check language')
                                    # print("                     ")
                                    try:
                                        lang = self.detect_lang(comment_original_language)
                                    except Exception as erreur:
                                        lang = "fr"
                                    if lang not in all_language:
                                        lang = "fr"
                                    
                                try:
                                    date_visit_content = card.find('div', {'class':'DmVtKb'}).text.strip()
                                except:
                                    date_visit_content = ""

                                match lang:
                                    case 'fr':
                                        print(f'date visite de {author} => {date_visit_content} (fr)') #04 02 2026 pour une visibilité car l'erreur sur serveur était ici
                                        date_visit = format_date_fr(date_visit_content) if date_visit_content else ""
                                if two_comment:
                                    # print("                     ")
                                    # print("take the comment traduct because we have two comment")
                                    # print("                     ")
                                    comment = comment_traduct
                                else:
                                    # print("             ")
                                    # print("we have only one comment, take this")
                                    # print("                     ")
                                    comment = comment_view_in_page
                        except Exception as e:
                            print("                     ")
                            input(f"Erreur in BLOC comment selector, check navigator => {e}")
                        #fin 20 02 2025
                        url = self.driver.current_url

                        rating = card.find('div', {'class': 'GDWaad'}).text.strip() if card.find('div', {'class': 'GDWaad'}) else rating
                        date_raw = card.find('span', {'class': 'iUtr1 CQYfx'}).text.lower()

                        if 'sur' in date_raw:
                            date_raw = date_raw[:date_raw.index(' sur')]
                        if 'on' in date_raw:
                            date_raw = date_raw[:date_raw.index(' on')]
                        if 'en' in date_raw:
                            date_raw = date_raw[:date_raw.index(' en')]

                        date_raw = date_raw.replace('il y a ', '').replace('\xa0', ' ').replace('hace ', '').replace('ago', '')
                    else:
                        print('other site')
                        continue

                else:
                    author = card.find('div', {'class': 'Vpc5Fe'}).text.strip() if card.find('div', {'class': 'Vpc5Fe'}) else ''
                    try:
                        comment = card.find('div', {'class': 'OA1nbd'}).text.strip().replace('(Traducido por Google) ', '').replace('\xa0... Ver más', '').replace(" En savoir plus", "") \
                            .replace('(Traduit par Google)', '').replace('(Traduce by Google)', '') if card.find('div', {'class': 'OA1nbd'}) else ''
                        if "Cuisine\xa0:" in comment:
                            comment = comment.split("Cuisine\xa0:")
                            comment = comment[0]
                        if comment and "avis d'origine" in comment:
                            comment = comment.split("(avis d'origine)")[-1] 
                        if comment and "(original)" in comment:
                            comment = comment.split("(original)")[-1]
                    except:
                        print('Google handball comment exception')
                        pass
                    rating = '/'.join(card.find('div', {'class': 'dHX2k'})['aria-label'].replace('\xa0', '').replace(
                        'Note: ', '').replace(',', '.').split(' sur')) if card.find('div', {'class': 'dHX2k'}) else rating
                    date_raw = card.find(
                        'span', {'class': 'y3Ibjb'}).text.lower().replace('\xa0', ' ')
                    
                    date_raw = date_raw.replace('il y a ', '').replace('\xa0', '').replace('hace ', '').replace('ago', '')
                try:
                    lang = self.detect_lang(comment)
                    #J'ai ajouté ce bout de code car des fois les personnes ne mettent pas de commentaire et c'est en "espace"
                    if lang == None or lang == "":
                        lang = self.lang
                except:
                    lang = self.lang
  
                date_review = self.formate_date(date_raw)
                if date_review != "" and date_review is not None:
                    #Pour les nouveau url ajoutés d'hotels :
                    if self.last_review_date == None:
                        if (author or comment ) and rating != "0" and datetime.strptime(date_review, '%d/%m/%Y') > datetime.now() - timedelta(days=365):
                            reviews.append({
                                'rating': rating,
                                'author': author,
                                'date_review': date_review,
                                'comment': comment,
                                'url': url,
                                'language': lang,
                                'source': urlparse(self.driver.current_url).netloc.split('.')[1],
                                'date_visit': date_visit if date_visit else date_review,
                                'establishment': f'/api/establishments/{self.establishment}',
                                'settings': f'/api/settings/{self.settings}',
                                'novisitday': "1"
                            })

                        if datetime.strptime(date_review, '%d/%m/%Y') < (datetime.now() - timedelta(days=365)):
                            print("last date valid reached")
                            # self.data = reviews
                            self.data_loaded = True
                    else:
                        #j'ai enlevé le timedelta days=1 car je ne sais pas si ça sert à quoi
                        # if (author or comment ) and rating != "0" and datetime.strptime(date_review, '%d/%m/%Y') > (datetime.now() - timedelta(days=365)) and (datetime.strptime(date_review, '%d/%m/%Y') > (datetime.strptime(self.last_review_date, '%d/%m/%Y') + timedelta(days=1))):
                        if (author or comment ) and rating != "0" and datetime.strptime(date_review, '%d/%m/%Y') > (datetime.now() - timedelta(days=365)) and (datetime.strptime(date_review, '%d/%m/%Y') >= (datetime.strptime(self.last_review_date, '%d/%m/%Y'))):
                            reviews.append({
                                'rating': rating,
                                'author': author,
                                'date_review': date_review,
                                'comment': comment,
                                'url': url,
                                'language': lang,
                                'source': urlparse(self.driver.current_url).netloc.split('.')[1],
                                'date_visit': date_visit if date_visit else date_review,
                                'establishment': f'/api/establishments/{self.establishment}',
                                'settings': f'/api/settings/{self.settings}',
                                'novisitday': "1"
                            })
                            print(f'{date_review} >> {self.last_review_date} , New review registred to save')

                        # if datetime.strptime(date_review, '%d/%m/%Y') < (datetime.now() - timedelta(days=365)) or (datetime.strptime(date_review, '%d/%m/%Y') > (datetime.strptime(self.last_review_date, '%d/%m/%Y') + timedelta(days=1))):
                        else:    
                            # print("last date valid reached")
                            # self.data = reviews
                            self.data_loaded = True
                        
                        """ Code teto avant 10 decembre 2024 (code Thierry)"""
                        # if datetime.strptime(date_review, '%d/%m/%Y') < (datetime.now() - timedelta(days=365)) or (datetime.strptime(date_review, '%d/%m/%Y') > (datetime.strptime(self.last_review_date, '%d/%m/%Y') + timedelta(days=1))):
                        #     print("last date valid reached")
                            # self.data = reviews
                            # self.data_loaded = True
                        """ Fin Code teto avant 10 decembre 2024 (code Thierry) """

                    #J'ai cmmenté le 10 12 2024
                    # if self.data_loaded:
                    #     self.data = reviews
                    #     return self.data J'ai commenté car ça me semble inutile (10 12 2024)
                else:
                    print('date format incorrect')
            # print(reviews)
            self.data = reviews
        except Exception as e:
            print(e)
            

# trp = Google(url="https://www.google.com/travel/search?gsas=1&ts=EggKAggDCgIIAxocEhoSFAoHCOgPEAgYEhIHCOgPEAgYExgBMgIQAA&qs=MhNDZ29JMHJiR3ZQQ0sxNEJ1RUFFOAI&ap=KigKEgmcw-RS3xY1wBEoPI0SLJ1LQBISCRp2zWogFjXAESg8jWepnUtAugEHcmV2aWV3cw&client=firefox-b-d&hl=fr-FR&ved=0CAAQ5JsGahcKEwiwhrLhj_yIAxUAAAAAHQAAAAAQFA",
#                 establishment=79, settings=267, env="PROD")
# trp.set_language('fr')
# trp.execute()
# print(trp.data)
# input('press enter to exit')
