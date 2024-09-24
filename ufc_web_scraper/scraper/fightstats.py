#Import libraries for web-scraping and saving to CSV file.
import requests
import bs4
import re
import csv
import os

#Define paths for url folder and scraped files folder
url_path = os.getcwd() + '/urls'
file_path = os.getcwd() + '/scraped_files'

def filter_duplicate_urls(fight_urls):
    if 'ufc_fight_stat_data.csv' in os.listdir(file_path):
        with open(file_path + '/' + 'ufc_fight_stat_data.csv','r') as csv_file:
            reader = csv.DictReader(csv_file)
            scraped_fight_urls = [row['fight_url'] for row in reader]
            for url in scraped_fight_urls:
                if url in fight_urls:
                    fight_urls.remove(url)

#Scrapes fighter name
def get_fighter_id(fight_soup,fight_stats,fighter):
    if fighter == 1:
        try:
            return fight_stats[0].text
        except:
            return fight_soup.select('a.b-fight-details__person-link')[0].text
        
    elif fighter == 2:
        try:
            return fight_stats[1].text
        except:
            return fight_soup.select('a.b-fight-details__person-link')[1].text

#Scrapes striking stats for specified fighter
def get_striking_stats(fight_stats,fighter):
    if fighter == 1:
        try:
            return (#Knockdowns
            fight_stats[2].text, 
            #Total strikes attempted
            fight_stats[8].text.split(' of ')[1],
            #Total strikes successful
            fight_stats[8].text.split(' of ')[0],
            #Significant strikes attempted
            fight_stats[4].text.split(' of ')[1],
            #Significant strikes successful
            fight_stats[4].text.split(' of ')[0])
        
        except:
            return (#Knockdowns
            'NULL', 
            #Total strikes attempted
            'NULL',
            #Total strikes successful
            'NULL',
            #Significant strikes attempted
            'NULL',
            #Significant strikes successful
            'NULL')
        
    elif fighter == 2:
        try:
            return (#Knockdowns
            fight_stats[3].text, 
            #Total strikes attempted
            fight_stats[9].text.split(' of ')[1],
            #Total strikes successful
            fight_stats[9].text.split(' of ')[0],
            #Significant strikes attempted
            fight_stats[5].text.split(' of ')[1],
            #Significant strikes successful
            fight_stats[5].text.split(' of ')[0])
        
        except:
            return (#Knockdowns
            'NULL', 
            #Total strikes attempted
            'NULL',
            #Total strikes successful
            'NULL',
            #Significant strikes attempted
            'NULL',
            #Significant strikes successful
            'NULL')

#Scrapes grappling stats for specified fighter
def get_grappling_stats(fight_stats,fighter):
    if fighter == 1:

        try:
            return (#Takedowns attempted
            fight_stats[10].text.split(' of ')[1],
            #Takedowns successful
            fight_stats[10].text.split(' of ')[0],
            #Submissions attempted
            fight_stats[14].text,
            #Reversals
            fight_stats[16].text,
            #Control time
            fight_stats[18].text)
        
        except:
            return (#Takedowns attempted
            'NULL',
            #Takedowns successful
            'NULL',
            #Submissions attempted
            'NULL',
            #Reversals
            'NULL',
            #Control time
            'NULL')
        
    elif fighter == 2:

        try:
            return (#Takedowns attempted
            fight_stats[11].text.split(' of ')[1],
            #Takedowns successful
            fight_stats[11].text.split(' of ')[0],
            #Submissions attempted
            fight_stats[15].text,
            #Reversals
            fight_stats[17].text,
            #Control time
            fight_stats[19].text)
        
        except:
            return (#Takedowns attempted
            'NULL',
            #Takedowns successful
            'NULL',
            #Submissions attempted
            'NULL',
            #Reversals
            'NULL',
            #Control time
            'NULL')


#Scrapes details of each UFC fight and appends to file 'ufc_fight_data.csv'
def scrape_fightstats():
    
    #Creates csv file for scraped data
    if 'ufc_fight_stat_data.csv' not in os.listdir(file_path):
        with open (file_path + '/' + 'ufc_fight_stat_data.csv','w',newline="",encoding='UTF8') as ufc_fighter_data:
            writer = csv.writer(ufc_fighter_data)
            writer.writerow(['fighter_id',
                             'knockdowns',
                             'total_strikes_att',
                             'total_strikes_succ',
                             'sig_strikes_att',
                             'sig_strikes_succ',
                             'takedown_att',
                             'takedown_succ',
                             'submission_att',
                             'reversals',
                             'ctrl_time',
                             'fight_url'])
        print('New File Created - ufc_fighter_data.csv')
    else:
        print('Scraping to Existing File - ufc_fighter_data.csv')

    #Get fight URLs from file
    if 'fight_urls.csv' in os.listdir(url_path):
        with open(url_path + '/' + 'fight_urls.csv','r') as fight_csv:
            reader = csv.reader(fight_csv)
            fight_urls = [row[0] for row in reader]
    else:
        print("Missing file: fight_urls.csv - try running 'get_urls.get_fight_urls'")

    #Remove urls that have been scraped already
    filter_duplicate_urls(fight_urls)
    
    urls_to_scrape = len(fight_urls)
    print(f'Scraping {urls_to_scrape} fights...')
    urls_scraped = 0
    
    with open(file_path + '/' + 'ufc_fight_stat_data.csv','a+') as csv_file:
        writer = csv.writer(csv_file)
    
        #Iterate through each fight_url to scrape fight stats
        for url in fight_urls:

            fight_url = requests.get(url)
            fight_soup = bs4.BeautifulSoup(fight_url.text,'lxml')
            
            try:
                fight_stats = fight_soup.select('p.b-fight-details__table-text')
                
                #Scrape fight stats for first fighter 
                fighter_name = get_fighter_id(fight_soup,fight_stats,1)
                (knockdowns,
                 total_strikes_att,
                 total_strikes_succ,
                 sig_strikes_att,
                 sig_strikes_succ) = get_striking_stats(fight_stats,1)
                (takedown_att,
                 takedown_succ,
                 submission_att,
                 reversals,
                 ctrl_time) = get_grappling_stats(fight_stats,1)

                
                #Add fight stats for first fighter to csv
                writer.writerow([fighter_name.strip(),
                                knockdowns.strip(),
                                total_strikes_att.strip(),
                                total_strikes_succ.strip(),
                                sig_strikes_att.strip(),
                                sig_strikes_succ.strip(),
                                takedown_att.strip(),
                                takedown_succ.strip(),
                                submission_att.strip(),
                                reversals.strip(),
                                ctrl_time.strip(),
                                url])

                #Scrape fight stats for second fighter 
                fighter_name = get_fighter_id(fight_soup,fight_stats,2)
                (knockdowns,
                 total_strikes_att,
                 total_strikes_succ,
                 sig_strikes_att,
                 sig_strikes_succ) = get_striking_stats(fight_stats,2)
                (takedown_att,
                 takedown_succ,
                 submission_att,
                 reversals,
                 ctrl_time) = get_grappling_stats(fight_stats,2)

                #Add fight stats for second fighter to csv
                writer.writerow([fighter_name.strip(),
                                knockdowns.strip(),
                                total_strikes_att.strip(),
                                total_strikes_succ.strip(),
                                sig_strikes_att.strip(),
                                sig_strikes_succ.strip(),
                                takedown_att.strip(),
                                takedown_succ.strip(),
                                submission_att.strip(),
                                reversals.strip(),
                                ctrl_time.strip(),
                                url])
                
                urls_scraped += 1
            except IndexError as e:
                print(f"Erro ao acessar elemento para a URL {url}: {e}")
                # Trate o erro adequadamente, como pular esta luta ou retornar valores padrão
        
    print(f'{urls_scraped}/{urls_to_scrape} links successfully scraped')

