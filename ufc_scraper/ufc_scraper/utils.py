from collections import defaultdict
from datetime import datetime
import re
from typing import Tuple, Dict, List
from uuid import uuid5, NAMESPACE_URL

from scrapy.http.response.html import HtmlResponse


def clean_string(raw_string: str) -> str:
    return re.sub(r'\s+', ' ', raw_string).strip()


def get_fighter_names(response: HtmlResponse) -> Dict[str, str]:
    fighter_names_dict = defaultdict()
    fighter_name_raw = response.css('span.b-content__title-highlight::text').get()
    fighter_name_clean = clean_string(fighter_name_raw)
    fighter_names = fighter_name_clean.split(' ')

    fighter_names_dict["full_name"] = ' '.join(fighter_names)
    fighter_names_dict["first_name"] = fighter_names[0]
    fighter_names_dict["last_names"] = ' '.join(fighter_names[1:])

    fighter_nickname_raw = response.css('p.b-content__Nickname::text').get()
    fighter_names_dict["nickname"] = clean_string(fighter_nickname_raw)

    return fighter_names_dict


def get_fighter_personal_stats(response: HtmlResponse, dob_format: str = "%Y-%m-%d") -> Dict[str, str]:
    fighter_stats_dict = defaultdict()
    fighter_stats = response.css('li.b-list__box-list-item::text').getall()

    fighter_height_raw = fighter_stats[1]
    fighter_height_clean = clean_string(fighter_height_raw)
    if fighter_height_clean == "--":
        fighter_height_ft = 0
        fighter_height_in = 0
        fighter_height_cm = float(0)
    else:
        fighter_height_ft = int(fighter_height_clean.split("'")[0])
        fighter_height_in = int(fighter_height_clean.split("'")[1].replace('"', '').strip())
        fighter_height_cm = float(((fighter_height_ft * 12.0) * 2.54) + (fighter_height_in * 2.54))

    fighter_weight_raw = fighter_stats[3]
    fighter_weight_clean = clean_string(fighter_weight_raw).replace('lbs.', '')
    if fighter_weight_clean == "--":
        fighter_weight_lbs = 0
    else:
        fighter_weight_lbs = int(fighter_weight_clean)

    fighter_reach_raw = fighter_stats[5]
    fighter_reach_clean = clean_string(fighter_reach_raw).replace('"', '')
    if fighter_reach_clean == "--":
        fighter_reach_in = 0
        fighter_reach_cm = 0
    else:
        fighter_reach_in = int(fighter_reach_clean)
        fighter_reach_cm = int(fighter_reach_clean) * 2.54

    fighter_stance_raw = fighter_stats[7]
    fighter_stance_clean = clean_string(fighter_stance_raw)

    fighter_dob_raw = fighter_stats[9]
    fighter_dob_clean = clean_string(fighter_dob_raw)
    if fighter_dob_clean == "--":
        fighter_dob = ""
    else:
        fighter_dob_dt = datetime.strptime(fighter_dob_clean, "%b %d, %Y")
        fighter_dob = datetime.strftime(fighter_dob_dt, dob_format)

    fighter_stats_dict["height_ft"] = fighter_height_ft
    fighter_stats_dict["height_in"] = fighter_height_in
    fighter_stats_dict["height_cm"] = fighter_height_cm
    fighter_stats_dict["weight_lbs"] = fighter_weight_lbs
    fighter_stats_dict["reach_in"] = fighter_reach_in
    fighter_stats_dict["reach_cm"] = fighter_reach_cm
    fighter_stats_dict["stance"] = fighter_stance_clean
    fighter_stats_dict["dob"] = fighter_dob

    return fighter_stats_dict


def get_fighter_record(response: HtmlResponse) -> Tuple[str, str, str, str]:
    fighter_record_dict = defaultdict()

    fighter_record_raw = response.css('span.b-content__title-record::text').get()
    fighter_record_clean = clean_string(fighter_record_raw)
    fighter_record = fighter_record_clean.split(': ')[1]
    fighter_record_dict["wins"] = int(fighter_record.split('-')[0])
    fighter_record_dict["losses"] = int(fighter_record.split('-')[1])

    # If a fighter has > 0 no contests, the record looks like 'Record: 28-1-0 (1 NC)'
    try:
        fighter_record_dict["draws"] = int(fighter_record.split('-')[2])
        fighter_record_dict["no_contests"] = 0
    except ValueError:
        fighter_record_dict["draws"] = int(fighter_record.split('-')[2].split(' ')[0])
        fighter_record_dict["no_contests"] = int(fighter_record.split('-')[2].split(' ')[1].replace('(', ''))

    return fighter_record_dict


def get_fighter_opponents(response: HtmlResponse) -> str:
    opponent_text_raw = response.css('a.b-link::text').getall()
    opponent_text_clean = [clean_string(opponent) for opponent in opponent_text_raw]
    opponent_urls = response.css('a.b-link::attr(href)').getall()
    fighter_url = response.url
    opponent_text_urls_list = list(zip(opponent_text_clean, opponent_urls))

    text_exclusion_list = [":", "ufc", "preview", "dwcs", "vs", "strikeforce", " - ", "pride", "dream"]
    opponent_urls_filtered = [
        opponent_url for opponent_name, opponent_url in opponent_text_urls_list
        if opponent_url != fighter_url
        and all(term not in opponent_name.lower() for term in text_exclusion_list)
    ]
    opponent_id_list = [
        str(uuid5(namespace=NAMESPACE_URL, name=opponent_url)) for opponent_url in opponent_urls_filtered
    ]

    return ", ".join(opponent_id_list)

def get_event_info(response: HtmlResponse, dob_format: str = "%Y-%m-%d") -> Dict[str, str]:
    event_info_dict: defaultdict = defaultdict()

    event_name_raw: str = response.css('span.b-content__title-highlight::text').get()
    event_name_clean: str = clean_string(event_name_raw)

    event_date_location: List[str] = response.css('li.b-list__box-list-item::text').getall()

    event_date_raw: str = event_date_location[1]
    event_date_clean: str = clean_string(event_date_raw)
    event_date_dt: datetime = datetime.strptime(event_date_clean, "%B %d, %Y")
    event_date: str = datetime.strftime(event_date_dt, dob_format)

    event_location_raw: str = event_date_location[3]
    event_location_clean: str = clean_string(event_location_raw)
    event_location_split: List[str] = event_location_clean.split(", ")
    if len(event_location_split) == 3:
        event_city: str = event_location_split[0]
        event_state: str = event_location_split[1]
        event_country: str = event_location_split[2]
    elif len(event_location_split) == 2:
        event_city: str = event_location_split[0]
        event_state: str = ""
        event_country: str = event_location_split[1]
    else:
        event_city: str = ""
        event_state: str = ""
        event_country: str = ""

    event_info_dict["name"] = event_name_clean
    event_info_dict["date"] = event_date
    event_info_dict["location"] = event_location_clean
    event_info_dict["city"] = event_city
    event_info_dict["state"] = event_state
    event_info_dict["country"] = event_country
    
    return event_info_dict