from scraping import Scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.command import Command
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from abc import abstractmethod
import sys
import json
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from langdetect import detect
from tools import month_number
from selenium.webdriver.support.select import Select
from models import Settings
from requests.models import PreparedRequest


class Booking(Scraping):
    def __init__(self, url: str, establishment: str, settings: str, env: str, last_review_date:str):
        defurl = url if url.endswith('.fr.html') else f"{url}.fr.html"
        super().__init__(in_background=False, 
                         url=defurl,
                         establishment=establishment, 
                         settings=settings, 
                         env=env,
                         last_review_date=last_review_date
                         )

    def set_language(self, language) -> None:
        super().set_language(language)
        url = self.url.split('?')[0]
        params = {'r_lang': self.lang, 'order': 'completed_desc'}
        req = PreparedRequest()
        req.prepare_url(url, params)
        super().set_url(req.url)
    
    #code de Thierry pour afficher toutes les reviews y compris les autres languages 04 08 2025
    def set_language(self, language) -> None:
        super().set_language(language)
        url = self.url.split('?')[0]
        # params = {'r_lang': self.lang, 'order': 'completed_desc'}
        params = {'r_lang': 'all', 'order': 'completed_desc'}
        req = PreparedRequest()
        req.prepare_url(url, params)
        super().set_url(req.url)

    def check_page(self) -> None:
        try:
            page_404 = self.driver.find_element(
                By.XPATH, "//div[@id='error404page']")
            Settings.disable_setting(self.setting_id, env=self.env)
            return False if page_404 else True
        except:
            return True
    #16 06 2026 : extract nouvel vue
    def extract_new_view(self):
        reviews = []
        print('nouvel affichage de booking, on saute cette url pour le moment en attendant de traiter le nouvel affichage')
        #Ajout paramètre en url #tab-reviews pour ne pas cliquer , #tab-main est automatiquement là , on le change par #tab-reviews 
        # input(f'url = {self.driver.current_url}')
        if "#tab-main" in self.driver.current_url:
            url_new = self.driver.current_url.replace("#tab-main", "#tab-reviews")
            self.driver.get(url_new)
            time.sleep(5)
        else:
            url_new = self.driver.current_url + "#tab-reviews"
            self.driver.get(url_new)
            time.sleep(5)
        print("         ")
        print('extraction sur la nouvelle view ...')
        print('         ')

        try:
            #selection d'affichage des reviews pour all languages 05 08 2025, tout est ALL déja sur la nouvelle view
            print('All languages sort OK')
            review_order = Select(self.driver.find_element(By.XPATH, "//select[@id='reviewListSorters']"))
            review_order.select_by_value('NEWEST_FIRST')
            time.sleep(0.8)
            # view_list_btn = self.driver.find_element(By.XPATH, "//div[@class='review_list_nav_wrapper clearfix']/form/input[@type='submit']")
            # self.driver.execute_script("arguments[0].click();", view_list_btn)
            print('Ordre des avis (les plus récents) sélectionné avec succès')
        except Exception as e:
            input(f"Erreur lors de la sélection de l'ordre des avis : {e}")
        
        #Sur cette nouvelle view, on peut voir un button voir la traduction, donc on va tous les cliqués pour traduire en français les reviews
        container_all_buttons_translations = self.driver.find_elements(By.CSS_SELECTOR, "div[data-testid='review-translation-handle']")
        # print(container_all_buttons_translations)
        for container_btn in container_all_buttons_translations:
            btn = container_btn.find_element(By.TAG_NAME, 'button')
            try:
                self.driver.execute_script("arguments[0].click();", btn)
            except Exception as e:
                input(f"Erreur lors du clic sur le bouton de traduction : {e}, checker le selecteur et relancer")
                self.driver.quit()
            time.sleep(1)
 
        print('         ')
        print(' Tous les boutons de traductions cliqués')
        print('         ')

        try:
            break_transmetter = True
            while True:
                time.sleep(5)

                page = self.driver.page_source
                # input('pause pour changement de langue manuel avant de donner à BS')
                soupe = BeautifulSoup(page, 'html.parser')

                review_cards = soupe.find_all('div', {'data-testid': 'review'}) 
                count = len(review_cards)

                print(f"====> {count} cards trouvés !")
                for card in review_cards:
                    try:
                        title = card.find('h4', {'data-testid': 'review_item_header_content'}).text.strip(
                        ) if card.find('h4', {'data-testid': 'review_item_header_content'}) else ""
                        
                        negative = card.find('div', {'data-testid': 'review-negative-text'}).text.strip(
                        ) if card.find('div', {'data-testid': 'review-negative-text'}) else ""
                        
                        positive = card.find('div', {'data-testid': 'review-positive-text'}).text.strip(
                        ) if card.find('div', {'data-testid': 'review-positive-text'}) else ""
                        
                        detail = f'{positive} | {negative}' if positive and negative else (
                            positive if positive else negative)
                        
                        comment = f"{title}{': ' if title and detail else ''}{detail}"

                        # input(f'Commentaire extrait : {comment}')

                        review_posted_date = card.find('span', {'data-testid': 'review-date'}).text.strip(
                        ) if card.find('span', {'data-testid': 'review-date'}) else ""
                        dates = review_posted_date.split()
                        # input(f'dates splittés: {dates}')

                        date_review = ""
                        
                        #A demander confirmation avec Nicolas pour voir si la langue de l'établissement est ES par exemple, est ce qu'on ne traduit pas les commentaires en ES maisn on laisse?
                        if self.lang == "es":
                            try:
                                #sur serveur c'est la date_review suivante:
                                date_review = f"{dates[-5]}/{month_number(dates[-3], 'es')}/{dates[-1]}"
                                #si dans mon local c'est la date review suivante (question d'affichage en langue de mon pc)
                                # date_review = f"{dates[-3]}/{month_number(dates[-2], 'fr')}/{dates[-1]}"
                            except Exception as e:
                                input(f"Erreur date_review formattage => {e}")
                        else:
                            try:
                                date_review = f"{dates[-3]}/{month_number(dates[-2], 'fr')}/{dates[-1]}"
                            except Exception as e:
                                date_review = f"{dates[-3]}/{month_number(dates[-2], 'en')}/{dates[-1]}"

                        if card.find('span', {'data-testid': 'review-stay-date'}):
                            date_séjour_brute = card.find('span', {'data-testid': 'review-stay-date'}).text.strip().split()[-2:]
                            #Normalement la lang est toujours fr car on n'est pas dans booking es, l'affichage de la page est en fr mais les reviews seulement puvent être en langue différents selon les clients
                            date_visit = f"{(datetime.now().day-1)}/{month_number(date_séjour_brute[0], 'fr')}/{date_séjour_brute[-1]}"
                        else:
                            date_visit = date_review

                        try:
                            # if self.lang and lang == self.lang:
                            try:
                                author_container = card.find('div', {'data-testid': 'review-avatar'}) if card.find('div', {'data-testid': 'review-avatar'}) else ""
                                author = author_container.find('div', {'class':'b08850ce41 f546354b44'}).text.strip() if author_container.find('div', {'class':'b08850ce41 f546354b44'}) else ""
                                rating_container = card.find('div', {'data-testid': 'review-score'}) if card.find('div', {'data-testid': 'review-score'}) else "0"
                                rating = rating_container.find('div',{'class', 'f63b14ab7a dff2e52086'}).text.strip() if rating_container.find('div',{'class', 'f63b14ab7a dff2e52086'}) else "0"
                            except Exception as e:
                                input(f"Erreur lors de l'extraction de l'auteur ou de la note => {e}")
                            
                            lang_source = {'Belgique':'be', 'France': 'fr', 'Italie': 'it', 'Pays-Bas' : 'nl', 'Brésil':'br', 'Portugal': 'pt','Autriche' : 'at', 'Suisse' : 'ch', 'Allemagne' : 'de', 'Australie' : 'au', 'Royaume-Uni' : 'uk', 'Estonie' : 'ee', 'Serbie' : 'sr', 'Suède' : 'se', 'Israël' : 'il', 'Bulgarie' : 'bg', 'Lituanie' : 'lt', 'Slovaquie' : 'sk', 'Irlande' : 'ie', 'Espagne' : 'es', 'Panama' : 'pa', 'Norvège' : 'no', 'Slovénie' : 'si', 'République tchèque' : 'cz'}
                            lang = author_container.find('span', {'class': 'd838fb5f41 aea5eccb71'}).text.strip()
                            if lang:
                                try:
                                    lang = lang_source[lang]
                                    
                                except Exception as e:
                                    print(e)
                                    lang = self.lang
                            
                            print('         ')
                            print(f'auteur => {author}, rating => {rating}, lang => {lang}, review => {comment}, date_review => {date_review}, date_visit => {date_visit}')
                            print('         ')

                            #04 08 2026 :remarque depuis monitoring , des dates ont des 'er' comme 1er, on les enlève car bloque le check
                            if 'er' in date_review:
                                date_review = date_review.replace('er', '')
                                print(f"date_review modifiée => {date_review}")
                            
                            if self.check_date(date_review, self.last_review_date):
                                print("             ")
                                print("On ajoute car la date du review est encore supérieur à celle dans la base")
                                print("             ")
                                reviews.append({
                                    'comment': comment,
                                    'rating': rating,
                                    'date_review': date_review,
                                    'language': lang,
                                    'url':self.driver.current_url,
                                    'source': urlparse(self.url).netloc.split('.')[1],
                                    'author': author,
                                    'establishment': f'/api/establishments/{self.establishment}',
                                    'settings': f'/api/settings/{self.settings}',
                                    'date_visit': date_review,
                                    'novisitday': "0"
                                })
                            else:
                                break_transmetter = False
                                break

                        except Exception as e:
                            input(f'pause , ERREUR == {e}')
                            continue

                    except Exception as e:
                        print(e)
                #ajout condition pour self.last_review_date
                print(f"la valeur du check date => {self.check_date(reviews[-1]['date_review'], self.last_review_date)}")
                if not break_transmetter:
                    break
                try:

                    next_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Page suivante"]')

                    if next_btn:
                        self.driver.execute_script("arguments[0].click();", next_btn)
                        time.sleep(4)

                except Exception as e:
                    input(f"Erreur lors de la recherche du bouton suivant : {e}")
                    break

        except Exception as e:
            print(f"erreur du while dans extract de booking => {e}")
            pass

        self.data = reviews

    def extract(self):
        
        if "https://www.booking.com/hotel" in self.driver.current_url: 
            self.extract_new_view() #16 06 2026
            return
        
        print('extraction ...')

        reviews = []

        try:
            #selection d'affichage des reviews pour all languages 05 08 2025
            show_all_languages_review = Select(self.driver.find_element(By.XPATH, '//*[@id="language"]'))
            show_all_languages_review.select_by_value('all')
            time.sleep(0.8)
            print('All languages sort OK')
            
            review_order = Select(self.driver.find_element(
                By.XPATH, "//select[@id='sorting']"))
            review_order.select_by_value('completed_desc')
            time.sleep(0.8)
            view_list_btn = self.driver.find_element(
                By.XPATH, "//div[@class='review_list_nav_wrapper clearfix']/form/input[@type='submit']")
            self.driver.execute_script("arguments[0].click();", view_list_btn)
            print('ordre des avis (les plus récents) sélectionné avec succès')
        except Exception as e:
            input(f"Erreur lors de la sélection de l'ordre des avis : {e}")
            return

        try:
            break_transmetter = True
            while True:
                time.sleep(5)

                page = self.driver.page_source
                # input('pause pour changement de langue manuel avant de donner à BS')
                soupe = BeautifulSoup(page, 'html.parser')

                review_cards = soupe.find_all('li', {'itemprop': 'review'})
                count = len(review_cards)

                print(f"====> {count} cards trouvés !")
                for card in review_cards:
                    try:
                        title = card.find('div', {'class': 'review_item_header_content'}).text.strip(
                        ) if card.find('div', {'class': 'review_item_header_content'}) else ""
                        negative = card.find('p', {'class': 'review_neg'}).text.strip(
                        ) if card.find('p', {'class': 'review_neg'}) else ""
                        positive = card.find('p', {'class': 'review_pos'}).text.strip(
                        ) if card.find('p', {'class': 'review_pos'}) else ""
                        detail = f'{positive} | {negative}' if positive and negative else (
                            positive if positive else negative)
                        comment = f"{title}{': ' if title and detail else ''}{detail}"

                        raw_date = card.find('p', {'class': 'review_item_date'}).text.strip(
                        ) if card.find('p', {'class': 'review_item_date'}) else ""
                        dates = raw_date.split()
                        print(dates)

                        date_review = ""

                        if self.lang == "es":
                            try:
                                #sur serveur c'est la date_review suivante:
                                date_review = f"{dates[-5]}/{month_number(dates[-3], 'es')}/{dates[-1]}"
                                #si dans mon local c'est la date review suivante (question d'affichage en langue de mon pc)
                                # date_review = f"{dates[-3]}/{month_number(dates[-2], 'fr')}/{dates[-1]}"
                            except Exception as e:
                                print(f"erreur date_review modification => {e}")
                                input('ETO')
                            # print(dates)
                            print(date_review)
                        else:
                            try:
                                date_review = f"{dates[-3]}/{month_number(dates[-2], 'fr')}/{dates[-1]}"
                            except Exception as e:
                                date_review = f"{dates[-3]}/{month_number(dates[-2], 'en')}/{dates[-1]}"

                        if card.find('p', {'class': 'review_staydate '}):
                            date_visit_raw = card.find(
                                'p', {'class': 'review_staydate '}).text.strip().split()[-2:]
                            date_visit = f"{(datetime().day-1)}/{month_number(date_visit_raw[0], 'en')}/{date_visit_raw[1]}"
                            print(date_visit)
                        else:
                            date_visit = date_review

                        try:
                            lang = detect(comment)
                        except:
                            lang = 'en'

                        try:
                            # if self.lang and lang == self.lang:
                            #ilay code booking amzao anaty serveur sy amle TENA IZY local mbola alainy daholo izay amle page actuel 
                            author = card.find('p', {'class': 'reviewer_name'}).text.strip() if card.find('p', {'class': 'reviewer_name'}) else ""
                            rating = card.find('span', {'class': 'review-score-badge'}).text.strip() if card.find('span', {'class': 'review-score-badge'}) else "0"
                            
                            #04 07 2025 : rating /2, all rating is /10 donc pas besoin de condition if rating > 10
                            # try:
                            #     input(f"format de la note => {rating}")
                            #     if '.' in rating:
                            #         # input('decimaal en point')
                            #         rating = float(rating)
                            #     if ',' in rating:
                            #         # input('decimaal en virgule, changement virgule par point')
                            #         rating = float(rating.replace(',', '.'))
                            #     rating = rating / 2
                            #     input(f"rating après conversion sur 5 => {rating}")
                            # except Exception as e:
                            #     print(f"erreur de conversion du rating => {e}")
                            #Code de Thierry semaine du 07 07 2025
                            lang_source = {'Belgique':'be', 'France': 'fr', 'Italie': 'it', 'Pays-Bas' : 'nl', 'Brésil':'br', 'Portugal': 'pt','Autriche' : 'at', 'Suisse' : 'ch', 'Allemagne' : 'de', 'Australie' : 'au', 'Royaume-Uni' : 'uk', 'Estonie' : 'ee', 'Serbie' : 'sr', 'Suède' : 'se', 'Israël' : 'il', 'Bulgarie' : 'bg', 'Lituanie' : 'lt', 'Slovaquie' : 'sk', 'Irlande' : 'ie', 'Espagne' : 'es', 'Panama' : 'pa', 'Norvège' : 'no', 'Slovénie' : 'si', 'République tchèque' : 'cz'}
                            lang = card.find('span', {'class': 'reviewer_country'}).find('span', {'itemprop':'name'}).text.strip()
                            if lang:
                                try:
                                    print(f"lang {lang} == {lang_source[lang]}")
                                    lang = lang_source[lang]
                                    
                                except Exception as e:
                                    print(e)
                                    lang = self.lang
                            #juste pour test en local ity:
                            # input({
                            #     'comment': comment,
                            #     'rating': rating,
                            #     'date_review': date_review,
                            #     'language': lang,
                            #     'url':self.driver.current_url,
                            #     'source': urlparse(self.url).netloc.split('.')[1],
                            #     'author': author,
                            #     'establishment': f'/api/establishments/{self.establishment}',
                            #     'settings': f'/api/settings/{self.settings}',
                            #     'date_visit': date_review,
                            #     'novisitday': "0"
                            #     })
                            
                            if self.check_date(date_review, self.last_review_date):
                                # print("             ")
                                # print("On ajoute car la date du review est encore supérieur à celle dans la base")
                                # print("             ")
                                reviews.append({
                                    'comment': comment,
                                    'rating': rating,
                                    'date_review': date_review,
                                    'language': lang,
                                    'url':self.driver.current_url,
                                    'source': urlparse(self.url).netloc.split('.')[1],
                                    'author': author,
                                    'establishment': f'/api/establishments/{self.establishment}',
                                    'settings': f'/api/settings/{self.settings}',
                                    'date_visit': date_review,
                                    'novisitday': "0"
                                })
                            else:
                                # input("date review est superieur à la last_review_date, on ne l'ajoute pas")
                                # input(f"date de la dernière review appender => {reviews[-1]['date_review']}")
                                break_transmetter = False
                                break

                                # print(f"reviews qui seront ajoutés dans la base, date last prise en compte => {reviews}")
                            # print({
                            #     'comment': comment,
                            #     'rating': rating,
                            #     'date_review': date_review,
                            #     'language': self.lang,
                            #     'url':self.driver.current_url,
                            #     'source': urlparse(self.url).netloc.split('.')[1],
                            #     'author': author,
                            #     'establishment': f'/api/establishments/{self.establishment}',
                            #     'settings': f'/api/settings/{self.settings}',
                            #     'date_visit': date_review,
                            #     'novisitday': "0"
                            # })
                        except Exception as e:
                            input('pause')
                            print(e)
                            continue

                    except Exception as e:
                        print(e)
                #ajout condition pour self.last_review_date
                print(f"la valeur du check date => {self.check_date(reviews[-1]['date_review'], self.last_review_date)}")
                if not break_transmetter:
                    # input("On ne clique plus sur le bouton suivant")
                    break
                try:

                    next_btn = self.driver.find_element(
                        By.ID, 'review_next_page_link')

                    if next_btn:
                        self.driver.execute_script(
                            "arguments[0].click();", next_btn)
                        time.sleep(4)

                except Exception as e:
                    input(f"Erreur lors de la recherche du bouton suivant : {e}")
                    break

        except Exception as e:
            print(f"Erreur lors de la recherche du bouton suivant : {e}")
            pass

        self.data = reviews

        with open('booking_test.json', 'w') as openfile:
            openfile.write(json.dumps(self.data, indent=4))


class Booking_ES(Booking):
    def __init__(self, url: str, establishment: str, settings: str, env: str, last_review_date : str):
        super().__init__(url=url, establishment=establishment, settings=settings, env=env, last_review_date=last_review_date)
        self.lang = "es"

{'id': 294, 'caption': '', 'section': '', 'external_url': None, 'establishment_name': 'LUX Saint Gilles', 'establishment_id': 79, 'establishment_tag': '66a0156222716', 'idprovider': 33, 'category': 'Platform', 'source': 'Booking', 'url': 'https://www.booking.com/reviews/re/hotel/lux-saint-gilles-resort.fr.html', 'language': 'en', 'last_review_date': '13/11/2024', 'last_comment_date': None, 'last_post_date': None}

# trp = Booking_ES(url="https://www.booking.com/reviews/es/hotel/antequera-golf.es.html?aid=356980\u0026customer_type=total\u0026order=completed_desc",
#                 establishment=27,
#                 settings=80,
#                 env='PROD',
#                 last_review_date='29/08/2024')
# trp.execute()
# print(trp.data)