#Import libraries for web-scraping and saving to CSV file
import requests
import bs4
import csv

#Scrapes url of each UFC event from ufcstats.com
def get_event_urls():
    main_url = requests.get('http://ufcstats.com/statistics/events/completed?page=all')
    main_event_soup = bs4.BeautifulSoup(main_url.text, 'lxml')
    
    #Adds href to list if href contains a link with keyword 'event-details'
    all_event_urls = [item.get('href') for item in  main_event_soup.find_all('a') 
                      if type(item.get('href')) == str 
                      and 'event-details' in item.get('href')]
    
    return all_event_urls

#Adds each link as a new row to a csv file
def save_to_file(links):
    with open('event_urls.csv','w',newline='') as event_urls:
        writer = csv.writer(event_urls)
        for link in links:
            writer.writerow([link])

event_urls = get_event_urls()
num_links = len(event_urls)
save_to_file(event_urls)
print(f'{num_links} links successfully scraped')





