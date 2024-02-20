from facebook_page_scraper import Facebook_scraper

# instantiate the Facebook_scraper class

page_name = "metaai"
posts_count = 10
browser = "chrome"
# if proxy requires authentication then user:password@IP:PORT
proxy = "driehlrt-rotate:hart9h8hysy6@p.webshare.io:80"
timeout = 600  # 600 seconds
headless = True
meta_ai = Facebook_scraper(page_name, posts_count, browser,
                           proxy=proxy, timeout=timeout, headless=headless)

# call the scrap_to_json() method

json_data = meta_ai.scrap_to_json()
print(json_data)
