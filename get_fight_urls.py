#Import libraries for web-scraping and saving to CSV file
import requests
import bs4
import csv
import os

#Get event URLs from file
if 'ufc_event_data.csv' in os.listdir():
    with open('event_urls.csv','r') as events_csv:
        reader = csv.reader(events_csv)
        event_urls = [row[0] for row in reader]
else:
    print("Missing file: event_urls.csv - try running 'get_event_urls.py'")

#Gets url for each fight in each event
def get_fight_urls(event_urls):
            
    all_fight_urls = []
    for url in event_urls:
        event_url = requests.get(url)
        event_soup = bs4.BeautifulSoup(event_url.text,'lxml')

        for item in event_soup.find_all('a', class_='b-flag b-flag_style_green'):
            all_fight_urls.append(item.get('href'))

    return all_fight_urls

#Adds each link as a new row to a csv file
def save_to_file(links):
    with open('fight_urls.csv','w',newline='') as fight_urls:
        writer = csv.writer(fight_urls)
        for link in links:
            writer.writerow([link])

print('Scraping fight links from ufcstats.com')
fight_urls = get_fight_urls(event_urls)
num_links = len(fight_urls)
save_to_file(fight_urls)
print(f'{num_links} links successfully scraped')




