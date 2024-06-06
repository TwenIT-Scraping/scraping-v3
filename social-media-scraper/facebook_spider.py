from playwright.sync_api import sync_playwright
from random import randint
from bs4 import BeautifulSoup
import time
from lingua import Language, LanguageDetectorBuilder
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.command import Command
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
import pytesseract
from PIL import Image
import base64
import io


TESSERACT_PATH = "C:/Users/Keller/AppData/Local/Programs/Tesseract-OCR"
pytesseract.pytesseract.tesseract_cmd = "C:/Program Files (x86)/pytesseract/tesseract.exe"


# binary_image = driver.find_element(By.CSS_SELECTOR, "span.xmper1u.xt0psk2.xjb2p0i.x1qlqyl8.x15bjb6t.x1n2onr6.x17ihmo5.x1g77sc7").screenshot_as_png
# pytesseract.image_to_string(Image.open(io.BytesIO(binary_image))).replace('\n', '')

class FacebookBaseScraper(object):

    def __init__(self) -> None:
        self.hotel_page_urls = []

        self.credentials = {
            'username': '',
            'password': 'Keller#pass4015',
            'phone': '0345861628'
        }

        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument(
            '--disable-blink-features=AutomationControlled')
        self.chrome_options.add_argument('--incognito')
        self.driver = webdriver.Chrome(options=self.chrome_options)


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

    def goto_login_page(self) -> None:
        self.driver.get('https://www.facebook.com')

    def resolve_login_forme(self) -> None:
        self.driver.find_element(By.XPATH, "//input[@data-testid='royal_email']").click()
        time.sleep(randint(1, 3))
        self.driver.find_element(By.XPATH, "//input[@data-testid='royal_email']").send_keys(self.credentials['phone'])
        time.sleep(randint(1, 3))
        self.driver.find_element(By.XPATH, "//input[@data-testid='royal_pass']").click()
        time.sleep(randint(1, 3))
        self.driver.find_element(By.XPATH, "//input[@data-testid='royal_pass']").send_keys(self.credentials['password'])
        time.sleep(randint(1, 3))
        self.driver.find_element(By.XPATH, "//button[@data-testid='royal_login_button']").click()
        time.sleep(randint(10, 20))

    def goto_page(self):
        self.driver.get("https://www.facebook.com/lidolacdubourget")
        time.sleep(randint(2, 5))
        comment_filter = self.driver.find_element(By.CSS_SELECTOR, "div.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1o1ewxj.x3x9cwd.x1e5q0jg.x13rtm0m.x1n2onr6.x87ps6o.x1lku1pv.x1a2a7pz")
        comment_filter.location_once_scrolled_into_view
        for i in range(2):
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)
        time.sleep(randint(1, 3))
        comment_filter.click()
        time.sleep(randint(1, 3))
        self.driver.find_elements(By.CSS_SELECTOR, "span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.xudqn12.x3x7a5m.x1f6kntn.xvq8zen.xk50ysn.xzsf02u.x1yc453h")[-1].click()
        # .last().click()
        time.sleep(randint(2, 4))

    def extract(self):
        self.driver.find_element(By.CSS_SELECTOR, "span.xmper1u.xt0psk2.xjb2p0i.x1qlqyl8.x15bjb6t.x1n2onr6.x17ihmo5.x1g77sc7").screenshot('test.png')

    def execute(self) -> None:
        self.goto_login_page()
        self.fill_login_forme()
        self.goto_page()
        self.extract()


FacebookBaseScraper().execute()