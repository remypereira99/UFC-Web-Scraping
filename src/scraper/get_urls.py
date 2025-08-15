#Import libraries for web-scraping and saving to CSV file
import requests
import bs4
import csv
import os
import time

# Helper function to write URLs to a CSV file
def write_urls_to_csv(file_name, urls):
    
    #Create a new directory for urls
    os.makedirs('urls',exist_ok=True)
    path = os.getcwd() + '/urls'
    
    #Save file to new directory and add urls to file
    with open(path + '/' + file_name, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for url in urls:
            writer.writerow([url])

#Scrapes url of each UFC event from ufcstats.com
def get_event_urls():
    
    print('Scraping event links from ufcstats.com')
    main_url = requests.get('http://ufcstats.com/statistics/events/completed?page=all')
    main_event_soup = bs4.BeautifulSoup(main_url.text, 'lxml')
    
    #Adds href to list if href contains a link with keyword 'event-details'
    all_event_urls = [item.get('href') for item in  main_event_soup.find_all('a') 
                      if type(item.get('href')) == str 
                      and 'event-details' in item.get('href')]
    
    #Creates csv file and adds each event url to file as a new row
    write_urls_to_csv('event_urls.csv', all_event_urls)

    print(len(all_event_urls), 'event links successfully scraped')
    

#Scrapes url of each UFC fight from ufcstats.com 
def get_fight_urls():

    #Get event URLs from file
    path = os.getcwd() + '/urls'
    
    if 'event_urls.csv' in os.listdir(path):
        with open(path + '/' + 'event_urls.csv','r') as events_csv:
            reader = csv.reader(events_csv)
            event_urls = [row[0] for row in reader]
    else:
        print("Unable to scrape ufc fights due to missing file 'event_urls.csv'. Try running 'get_event_urls.py'")
        return

    
        
    print('Scraping fight links from ufcstats.com')

    #Iterates through each event URL
    all_fight_urls = []
    for url in event_urls:
        event_url = requests.get(url)
        event_soup = bs4.BeautifulSoup(event_url.text,'lxml')

       #Scrapes fight URLs from event pages and adds to list
        for item in event_soup.find_all('a', class_='b-flag b-flag_style_green'):
            all_fight_urls.append(item.get('href'))


    #Creates csv file and adds each fight url to file as a new row
    write_urls_to_csv('fight_urls.csv', all_fight_urls)

    print(len(all_fight_urls), 'fight links successfully scraped')
    

#Scrapes url of each UFC fighter from ufcstats.com
def get_fighter_urls():

    print('Scraping fighter links from ufcstats.com')

    #Creates a list of each fighter page alphabetically
    main_url_list = []
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        main_url_list.append(requests.get(f'http://ufcstats.com/statistics/fighters?char={letter}&page=all'))
        #Adds 1s delay to avoid response(429)
        time.sleep(1)
        
    #Iterates through each page and scrapes fighter links
    main_soup_list = [bs4.BeautifulSoup(url.text,'lxml') for url in main_url_list]
    fighter_urls = []
    for main_link in main_soup_list:
        for link in main_link.select('a.b-link')[1::3]:
            fighter_urls.append(link.get('href'))

    #Adds each link as a new row to a csv file
    write_urls_to_csv('fighter_urls.csv', fighter_urls)

    print(len(fighter_urls),'links successfully scraped')
