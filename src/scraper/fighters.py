#Import libraries for web-scraping and saving to CSV file.
import requests
import bs4
import re
import csv
from string import ascii_lowercase
import os
from datetime import datetime

#Define paths for url folder and scraped files folder
url_path = os.getcwd() + '/urls'
file_path = os.getcwd() + '/scraped_files'

#If file does not exist, create a new CSV file with column headers
def create_csv():
    if 'ufc_fighter_data.csv' not in os.listdir(file_path):
        with open(file_path + '/' + 'ufc_fighter_data.csv','w',newline='',encoding='UTF8') as ufc_fighter_data:
            writer = csv.writer(ufc_fighter_data)
            writer.writerow(['fighter_f_name',
                             'fighter_l_name',
                             'fighter_nickname',
                             'fighter_height_cm',
                             'fighter_weight_lbs',
                             'fighter_reach_cm',
                             'fighter_stance',
                             'fighter_dob',
                             'fighter_w',
                             'fighter_l',
                             'fighter_d',
                             'fighter_nc_dq',
                             'fighter_url'])
        print('New File Created - ufc_fighter_data.csv')
    else:
        print('Scraping to Existing File - ufc_fighter_data.csv')

#Ensure each url is only scraped once when script is run multiple times
def filter_duplicate_urls(fighter_urls):
    if 'ufc_fighter_data.csv' in os.listdir(file_path):
        with open(file_path + '/' + 'ufc_fighter_data.csv','r') as csv_file:
            reader = csv.DictReader(csv_file)
            scraped_fighter_urls = [row['fighter_url'] for row in reader]
            
            #Removes previously scraped urls from fighter_urls
            for url in scraped_fighter_urls:
                if url in fighter_urls:
                    fighter_urls.remove(url)


#Parse fighter last name depending on length of name
def parse_l_name(name):
    if len(name) == 2:
        return name[-1]
    elif len(name) == 1:
        return 'NULL'
    elif len(name) == 3:
        return name[-2] + ' ' + name[-1]
    elif len(name) == 4:
        return name[-3] + ' ' + name[-2] + ' ' + name[-1]
    else:
        return 'NULL'


def parse_nickname(nickname):
    if nickname.text == '\n':
        return 'NULL'
    else:
        return nickname.text.strip()


#Converts height in feet/inches to height in cm
def parse_height(height):
    height_text = height.text.split(':')[1].strip()
    if '--' in height_text.split("'"):
        return 'NULL'
    else:
        height_ft = height_text[0]
        height_in = height_text.split("'")[1].strip().strip('"')
        height_cm = ((int(height_ft) * 12.0) * 2.54) + (int(height_in) * 2.54)
        return height_cm


#Converts reach in inches to reach in cm
def parse_reach(reach):
    reach_text = reach.text.split(':')[1]
    if '--' in reach_text:
        return 'NULL'
    else:
        return round(int(reach_text.strip().strip('"')) * 2.54, 2)


def parse_weight(weight_element):
    weight_text = weight_element.text.split(':')[1]
    if '--' in weight_text:
        return 'NULL'
    else:
        return weight_text.split()[0].strip()


def parse_stance(stance):
    stance_text = stance.text.split(':')[1]
    if stance_text == '':
        return 'NULL'
    else:
        return stance_text.strip()


#Converts string containing date of birth to datetime object
def parse_dob(dob):
    dob_text = dob.text.split(':')[1].strip()
    if dob_text == '--':
        return 'NULL'
    else:
        return str(datetime.strptime(dob_text, '%b %d, %Y'))[0:10]


#Scrapes details of each UFC fighter appends to CSV file 'ufc_fighter_data'
def scrape_fighters():
    
    #Get fighter URLs from file
    if 'fighter_urls.csv' in os.listdir(url_path):
        with open(url_path + '/' + 'fighter_urls.csv','r') as fighters_csv:
            reader = csv.reader(fighters_csv)
            fighter_urls = [row[0] for row in reader]
    else:
        print("Missing file: fighter_urls.csv - try running 'get_urls.get_fighter_urls()'")

    #Remove urls that have been scraped already
    filter_duplicate_urls(fighter_urls)
    
    urls_to_scrape = len(fighter_urls)

    if urls_to_scrape == 0:
        print('Fighter data already scraped.')

    else:

        create_csv()

        urls_scraped = 0
        
        print(f'Scraping {urls_to_scrape} fighters...')

        with open(file_path + '/' + 'ufc_fighter_data.csv', 'a+') as ufc_fighters:
            writer = csv.writer(ufc_fighters)

            #Iterates through each url and scrapes key details
            for url in fighter_urls:
                try:
                    fighter_url = requests.get(url)
                    fighter_soup = bs4.BeautifulSoup(fighter_url.text, 'lxml')
                    
                    name = fighter_soup.select('span')[0].text.split()
                    nickname = fighter_soup.select('p.b-content__Nickname')[0]
                    details = fighter_soup.select('li.b-list__box-list-item')
                    record = fighter_soup.select('span.b-content__title-record')[0].text.split(':')[1].strip().split('-')

                    fighter_f_name = name[0] 
                    fighter_l_name = parse_l_name(name)
                    fighter_nickname = parse_nickname(nickname)
                    fighter_height_cm = parse_height(details[0])
                    fighter_weight_lbs = parse_weight(details[1])
                    fighter_reach_cm = parse_reach(details[2])
                    fighter_stance = parse_stance(details[3])
                    fighter_dob = parse_dob(details[4])
                    fighter_w = record[0]
                    fighter_l = record[1]
                    fighter_d = record[-1][0] if len(record[-1]) > 1 else record[-1]
                    fighter_nc_dq = record[-1].split('(')[-1][0] if len(record[-1]) > 1 else 'NULL'
                    

                    #Adds new row to csv file
                    writer.writerow([fighter_f_name.strip(), 
                                     fighter_l_name.strip(), 
                                     fighter_nickname,
                                     fighter_height_cm,
                                     fighter_weight_lbs,
                                     fighter_reach_cm,
                                     fighter_stance,
                                     fighter_dob[0:10],
                                     fighter_w,
                                     fighter_l,
                                     fighter_d,
                                     fighter_nc_dq,
                                     url])
                    
                    urls_scraped += 1
                    
                except IndexError as e:
                    print(f"Error scraping fighter page: {url}")
                    print(f"Error details: {e}")


        print(f'{urls_scraped}/{urls_to_scrape} fighters scraped successfully')

