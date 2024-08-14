import subprocess
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

proxy_address = "socks5://127.0.0.1:9150"

chrome_path = "C:/Program Files/Google/Chrome/Application/chrome" 

subprocess.Popen([
    chrome_path,
    f'--proxy-server={proxy_address}',
    '--remote-debugging-port=9222',  
    '--no-sandbox',  
    '--disable-dev-shm-usage',  
])

time.sleep(10)  

chrome_options = Options()
chrome_options.debugger_address = '127.0.0.1:9222'

try:
    driver = webdriver.Chrome(options=chrome_options)
    
    url = "https://www.tripadvisor.fr/AttractionsNear-g23547400-d316478-Royal_Nozha_Hotel-Mrezga_Hammamet_Nabeul_Governorate.html"
    driver.get(url)
    time.sleep(10)

finally:
    # Close the browser
    driver.quit()
