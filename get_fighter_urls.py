#Import libraries for web-scraping and saving to CSV file
import requests
import bs4
import csv
from string import ascii_lowercase

#Scrapes url of each UFC fighter from ufcstats.com
def get_fighter_urls():
    main_url_list = [requests.get(f'http://ufcstats.com/statistics/fighters?char={letter}&page=all') for letter in ascii_lowercase]
    main_soup_list = [bs4.BeautifulSoup(url.text,'lxml') for url in main_url_list]
    all_links = []
    
    for main_link in main_soup_list:
        for link in main_link.select('a.b-link')[1::3]:
            all_links.append(link.get('href'))

    return all_links

#Adds each link as a new row to a csv file
def save_to_file(links):
    with open('fighter_urls.csv','w',newline='') as fighter_urls:
        writer = csv.writer(fighter_urls)
        for link in links:
            writer.writerow([link])

fighter_urls = get_fighter_urls()
num_links = len(fighter_urls)
save_to_file(fighter_urls)
print(f'{num_links} links successfully scraped')
