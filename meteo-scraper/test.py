from datetime import datetime


if __name__ == '__main__':
    now = datetime.now()
    with open('/var/www/scraping-v3/meteo-scraper/test.txt', 'w', encoding='utf-8') as file:
        file.write(now.strftime("%d/%m/%Y %H:%M:%S"))
