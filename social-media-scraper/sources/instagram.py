from instascrape import *


google = Profile('https://www.instagram.com/thedominickhotel/')

# Scrape their respective data 
google.scrape()


print(google.followers)
