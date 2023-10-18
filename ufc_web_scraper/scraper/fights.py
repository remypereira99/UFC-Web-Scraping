#Import libraries for web-scraping and saving to CSV file.
import requests
import bs4
import re
import csv
import os

#Define paths for url folder and scraped files folder
url_path = os.getcwd() + '/urls'
file_path = os.getcwd() + '/scraped_files'

#Creates csv file for scraped data
def create_csv_file():
    #If file does not exist, create a new CSV file with column headers
    if 'ufc_fight_data.csv' not in os.listdir(file_path):
        with open(file_path + '/' + 'ufc_fight_data.csv','w',newline='',encoding='UTF8') as ufc_fight_data:
            writer = csv.writer(ufc_fight_data)
            writer.writerow(['event_name', 
                             'referee', 
                             'f_1', 
                             'f_2', 
                             'winner', 
                             'num_rounds', 
                             'title_fight',
                             'weight_class', 
                             'gender',
                             'result', 
                             'result_details', 
                             'finish_round', 
                             'finish_time', 
                             'fight_url'])
        print('New File Created - ufc_fight_data.csv')
    else:
        print('Scraping to Existing File - ufc_fight_data.csv')

#Ensure each url is only scraped once when script is run multiple times
def filter_duplicate_urls(fight_urls):
    if 'ufc_fight_data.csv' in os.listdir(file_path):
        with open(file_path + '/' + 'ufc_fight_data.csv','r') as csv_file:
            reader = csv.DictReader(csv_file)
            scraped_fight_urls = [row['fight_url'] for row in reader]
            
            #Removes previously scraped urls from fight_urls
            for url in scraped_fight_urls:
                if url in fight_urls:
                    fight_urls.remove(url)

#Scrape referee name
def get_referee(overview):
    try:
        return overview[3].text.split(':')[1]
    except:
        return 'NULL'

#Scrape both fighter names
def get_fighters(fight_details,fight_soup):
    try:
        return fight_details[0].text, fight_details[1].text
    except:
        return fight_soup.select('a.b-fight-details__person-link')[0].text, fight_soup.select('a.b-fight-details__person-link')[1].text

#Scrape name of winner 
def get_winner(win_lose):
    #If there is a winner, set 'winner' to winning fighter. If no winner (e.g. NC, DQ) set 'winner' to NULL
    if (win_lose[0].text.strip()=='W') | (win_lose[1].text.strip()=='W'):
        if (win_lose[0].text.strip()=='W'):
            return f_1
        else:
            return f_2
    else:
        return 'NULL'

#Checks if fight is title fight
def get_title_fight(fight_type):
    if 'Title' in fight_type[0].text:
        return 'T'
    else:
        return 'F'

#Scrapes weight class of fight
def get_weight_class(fight_type):
    if 'Light Heavyweight' in fight_type[0].text.strip():
        return 'Light Heavyweight'
        
    elif 'Women' in fight_type[0].text.strip():
        return "Women's " + re.findall('\w*weight',fight_type[0].text.strip())[0]
        
    elif 'Catch Weight' in fight_type[0].text.strip():
        return 'Catch Weight'
            
    elif 'Open Weight' in fight_type[0].text.strip():
        return 'Open Weight'
            
    else:   
        try:
            return re.findall('\w*weight',fight_type[0].text.strip())[0]
        except: 
            return 'NULL'

#Checks gender of fight 
def get_gender(fight_type):
    if 'Women' in fight_type[0].text:
        return 'F'
    else:
        return 'M'

#Scrapes the way the fight ended (e.g. KO, decision, etc.)
def get_result(select_result,select_result_details):
    if 'Decision' in select_result[0].text.split(':')[1]:
        return select_result[0].text.split(':')[1].split()[0], select_result[0].text.split(':')[1].split()[-1]
    else:
        return select_result[0].text.split(':')[1], select_result_details[1].text.split(':')[-1]

#Scrapes details of each UFC fight and appends to file 'ufc_fight_data.csv'
def scrape_fights():
    
    #Get fight URLs from file
    if 'fight_urls.csv' in os.listdir(url_path):
        with open(url_path + '/' + 'fight_urls.csv','r') as fight_csv:
            reader = csv.reader(fight_csv)
            fight_urls = [row[0] for row in reader]
    else:
        print("Missing file: fight_urls.csv - try running 'get_urls.get_fight_urls()'")

    filter_duplicate_urls(fight_urls)
    
    urls_to_scrape = len(fight_urls)
    
    if urls_to_scrape == 0:
        print('Fight data already scraped')
        
    else:
        create_csv_file()

        print(f'Scraping {urls_to_scrape} fights...')
        urls_scraped = 0
    
        with open(file_path + '/' + 'ufc_fight_data.csv','a+') as csv_file:
            writer = csv.writer(csv_file)
        
            for url in fight_urls:

                fight_url = requests.get(url)
                fight_soup = bs4.BeautifulSoup(fight_url.text,'lxml')

                #Define key select statements
                overview = fight_soup.select('i.b-fight-details__text-item')
                select_result = fight_soup.select('i.b-fight-details__text-item_first')
                select_result_details = fight_soup.select('p.b-fight-details__text')
                fight_details = fight_soup.select('p.b-fight-details__table-text')
                fight_type = fight_soup.select('i.b-fight-details__fight-title')
                win_lose = fight_soup.select('i.b-fight-details__person-status')

                #Scrape fight details
                event_name = fight_soup.h2.text
                referee = get_referee(overview)
                f_1,f_2 = get_fighters(fight_details,fight_soup)
                num_rounds = overview[2].text.split(':')[1].strip()[0]
                title_fight = get_title_fight(fight_type)
                weight_class = get_weight_class(fight_type)
                gender = get_gender(fight_type)  
                result,result_details = get_result(select_result,select_result_details)
                finish_round = overview[0].text.split(':')[1]
                finish_time = re.findall('\d:\d\d',overview[1].text)[0]
                if (win_lose[0].text.strip()=='W') | (win_lose[1].text.strip()=='W'):
                    if (win_lose[0].text.strip()=='W'):
                        winner = f_1
                    else:
                        winner = f_2
                else:
                    winner = 'NULL'


                #Adds row containing scraped fight details to csv file
                writer.writerow([event_name.strip(),
                                 referee.strip(), 
                                 f_1.strip(), 
                                 f_2.strip(), 
                                 winner.strip(), 
                                 num_rounds.strip(), 
                                 title_fight,
                                 weight_class, 
                                 gender,
                                 result.strip(), 
                                 result_details.strip(), 
                                 finish_round.strip(), 
                                 finish_time.strip(), 
                                 url])
                
                urls_scraped += 1
        
        print(f'{urls_scraped}/{urls_to_scrape} links scraped successfully')
