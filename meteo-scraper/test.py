from datetime import datetime
import os


if __name__ == '__main__':
    now = datetime.now()
    if os.path.exists('/var/www/scraping-v3/meteo-scraper/test.txt'):
        with open('/var/www/scraping-v3/meteo-scraper/test.txt', 'a', encoding='utf-8') as file:
            file.write(now.strftime("%d/%m/%Y %H:%M:%S")+'\n')
    else:
        with open('/var/www/scraping-v3/meteo-scraper/test.txt', 'w', encoding='utf-8') as file:
            file.write(now.strftime("%d/%m/%Y %H:%M:%S")+'\n')
