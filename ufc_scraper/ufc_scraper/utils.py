from collections import defaultdict
from datetime import datetime
import re
from typing import Tuple, Dict, List, Union
from uuid import uuid5, NAMESPACE_URL

from scrapy.http.response.html import HtmlResponse

from ufc_scraper.constants import WEIGHT_CLASSES_LOWER


def clean_string(raw_string: str) -> str:
    return re.sub(r'\s+', ' ', raw_string).strip()


def get_uuid_string(input_string: str) -> str:
    return str(uuid5(namespace=NAMESPACE_URL, name=input_string))


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
        get_uuid_string(opponent_url) for opponent_url in opponent_urls_filtered
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


def get_event_fights(response: HtmlResponse) -> str:
    fight_urls: List[str] = response.css('a.b-flag::attr(href)').getall()
    fight_ids: List[str] = [
        get_uuid_string(fight_url) for fight_url in fight_urls
    ]

    return ", ".join(fight_ids)


def get_fighters(response: HtmlResponse) -> Dict[str, str]:
    fighter_dict: defaultdict = defaultdict()

    all_urls: List[str] = response.css('a.b-link::attr(href)').getall()
    fighter_a_url: str = all_urls[1]
    fighter_b_url: str = all_urls[2]

    fighter_a_id: str = get_uuid_string(fighter_a_url)
    fighter_b_id: str = get_uuid_string(fighter_b_url)

    fighter_dict["fighter_a_id"] = fighter_a_id
    fighter_dict["fighter_b_id"] = fighter_b_id

    return fighter_dict


def get_weight_class(bout_type: str) -> str:
    weight_class = ""
    for weight_class_lower in WEIGHT_CLASSES_LOWER:
        if weight_class_lower in bout_type.lower():
            weight_class = weight_class_lower

    return weight_class


def get_judges_decisions(response: HtmlResponse) -> Dict[str, str]:
    judge_decision_dict: defaultdict = defaultdict()

    judges_raw: List[str] = response.css('i.b-fight-details__text-item').xpath('./span/text()').getall()[1:]
    judges_clean: List[str] = [clean_string(judge) for judge in judges_raw]
    judge_decision_dict["judge_a"] = judges_clean[0]
    judge_decision_dict["judge_b"] = judges_clean[1]
    judge_decision_dict["judge_c"] = judges_clean[2]

    score_regex = r"\d{2} - \d{2}\."
    scores_raw: List[str] = response.css('i.b-fight-details__text-item::text').getall()
    scores_clean: List[str] = [
        clean_string(score).replace(".", "") for score in scores_raw if re.search(score_regex, score)
    ]
    judge_a_score, judge_b_score, judge_c_score = scores_clean
    judge_scores = zip(["judge_a", "judge_b", "judge_c"], [judge_a_score, judge_b_score, judge_c_score])
    for judge, score in judge_scores:
        judge_decision_dict[f"{judge}_fighter_a_score"] = int(score.split(" - ")[0])
        judge_decision_dict[f"{judge}_fighter_b_score"] = int(score.split(" - ")[1])

    return judge_decision_dict


def get_fight_info(response: HtmlResponse) -> Dict[str, str]:
    fight_dict: defaultdict = defaultdict()

    bout_type_raw: str = response.css("i.b-fight-details__fight-title::text").get()
    bout_type_clean: str = clean_string(bout_type_raw)
    weight_class: str = get_weight_class(bout_type_clean)

    time_format_raw: str = response.css('.b-fight-details__label:contains("Time format:")').xpath('./parent::*/text()').getall()[1]
    time_format_clean: str = clean_string(time_format_raw)
    num_rounds = int(time_format_clean.split(" ")[0])

    finish_method_raw: str = response.css('.b-fight-details__label:contains("Method:") + i::text').get()
    finish_method_clean: str = clean_string(finish_method_raw)
    judges_decisions: Dict[str, Union[str, int]] = {
        "judge_a": "",
        "judge_b": "",
        "judge_c": "",
        "judge_a_fighter_a_score": 0,
        "judge_a_fighter_b_score": 0,
        "judge_b_fighter_a_score": 0,
        "judge_b_fighter_b_score": 0,
        "judge_c_fighter_a_score": 0,
        "judge_c_fighter_b_score": 0,
    }
    if finish_method_clean.split(" ")[0].lower() == "decision":
        decision: List[str] = finish_method_clean.split(" - ")
        finish_method: str = decision[0].lower()
        finish_submethod_clean: str = decision[1].lower()

        judges_decisions: Dict[str, Union[str, int]] = get_judges_decisions(response)
    else:
        finish_method = finish_method_clean.lower()
        finish_submethod_raw: str = (
            response
            .css('.b-fight-details__label:contains("Details:")')
            .xpath('./ancestor::p/text()[normalize-space()]')
            .get()
        )
        finish_submethod_clean: str = clean_string(finish_submethod_raw)

    finish_round_raw: str = response.css('.b-fight-details__label:contains("Round:")').xpath('./parent::*/text()').getall()[1]
    finish_round_clean: int = int(clean_string(finish_round_raw))

    finish_time_raw: str = response.css('.b-fight-details__label:contains("Time:")').xpath('./parent::*/text()').getall()[1]
    finish_time_clean: str = clean_string(finish_time_raw)
    finish_time_minute: int = int(finish_time_clean.split(":")[0])
    finish_time_second: int = int(finish_time_clean.split(":")[1])

    referee_raw: str = response.css('.b-fight-details__label:contains("Referee:") + span::text').get()
    referee_clean: str = clean_string(referee_raw)

    fight_dict["weight_class"] = weight_class
    fight_dict["num_rounds"] = num_rounds
    fight_dict["finish_method"] = finish_method
    fight_dict["finish_submethod"] = finish_submethod_clean
    fight_dict["finish_round"] = finish_round_clean
    fight_dict["finish_time"] = finish_time_clean
    fight_dict["finish_time_minute"] = finish_time_minute
    fight_dict["finish_time_second"] = finish_time_second
    fight_dict["referee"] = referee_clean

    for key in judges_decisions.keys():
        fight_dict[key] = judges_decisions[key]

    return fight_dict


def get_fight_stats_from_summary(fight_stat_summary: str) -> Tuple[int, int]:
    fight_stat_summary_split: List[str] = clean_string(fight_stat_summary).split(" of ")
    landed = int(fight_stat_summary_split[0])
    attempted = int(fight_stat_summary_split[1])

    return landed, attempted


def get_fight_stats(response: HtmlResponse) -> Dict[str, str]:
    fight_stats_dict: defaultdict = defaultdict()

    fight_stat_summary: List[str] = response.css('p.b-fight-details__table-text::text').getall()

    fighter_a_knockdowns: int = int(clean_string(fight_stat_summary[4]))
    fighter_b_knockdowns: int = int(clean_string(fight_stat_summary[5]))
    (
        fighter_a_significant_strikes_landed,
        fighter_a_significant_strikes_attempted
    ) = get_fight_stats_from_summary(fight_stat_summary[6])
    (
        fighter_b_significant_strikes_landed,
        fighter_b_significant_strikes_attempted
    ) = get_fight_stats_from_summary(fight_stat_summary[7])
    (
        fighter_a_total_strikes_landed,
        fighter_a_total_strikes_attempted
    ) = get_fight_stats_from_summary(fight_stat_summary[10])
    (
        fighter_b_total_strikes_landed,
        fighter_b_total_strikes_attempted
    ) = get_fight_stats_from_summary(fight_stat_summary[11])
    (
        fighter_a_takedowns_landed,
        fighter_a_takedowns_attempted
    ) = get_fight_stats_from_summary(fight_stat_summary[12])
    (
        fighter_b_takedowns_landed,
        fighter_b_takedowns_attempted
    ) = get_fight_stats_from_summary(fight_stat_summary[13])
    fighter_a_submissions_attempted: int = int(fight_stat_summary[16])
    fighter_b_submissions_attempted: int = int(fight_stat_summary[17])
    fighter_a_reversals: int = int(fight_stat_summary[18])
    fighter_b_reversals: int = int(fight_stat_summary[19])
    fighter_a_control_time_raw: str = clean_string(fight_stat_summary[20])
    fighter_b_control_time_raw: str = clean_string(fight_stat_summary[21])
    fighter_a_control_time_minutes: int = int(fighter_a_control_time_raw.split(":")[0])
    fighter_b_control_time_minutes: int = int(fighter_b_control_time_raw.split(":")[0])
    fighter_a_control_time_seconds: int = int(fighter_a_control_time_raw.split(":")[1])
    fighter_b_control_time_seconds: int = int(fighter_b_control_time_raw.split(":")[1])

    fight_stats_dict["fighter_a_knockdowns"] = fighter_a_knockdowns
    fight_stats_dict["fighter_b_knockdowns"] = fighter_b_knockdowns
    fight_stats_dict["fighter_a_significant_strikes_landed"] = fighter_a_significant_strikes_landed
    fight_stats_dict["fighter_a_significant_strikes_attempted"] = fighter_a_significant_strikes_attempted
    fight_stats_dict["fighter_b_significant_strikes_landed"] = fighter_b_significant_strikes_landed
    fight_stats_dict["fighter_b_significant_strikes_attempted"] = fighter_b_significant_strikes_attempted
    fight_stats_dict["fighter_a_total_strikes_landed"] = fighter_a_total_strikes_landed
    fight_stats_dict["fighter_a_total_strikes_attempted"] = fighter_a_total_strikes_attempted
    fight_stats_dict["fighter_b_total_strikes_landed"] = fighter_b_total_strikes_landed
    fight_stats_dict["fighter_b_total_strikes_attempted"] = fighter_b_total_strikes_attempted
    fight_stats_dict["fighter_a_takedowns_landed"] = fighter_a_takedowns_landed
    fight_stats_dict["fighter_a_takedowns_attempted"] = fighter_a_takedowns_attempted
    fight_stats_dict["fighter_b_takedowns_landed"] = fighter_b_takedowns_landed
    fight_stats_dict["fighter_b_takedowns_attempted"] = fighter_b_takedowns_attempted
    fight_stats_dict["fighter_a_submissions_attempted"] = fighter_a_submissions_attempted
    fight_stats_dict["fighter_b_submissions_attempted"] = fighter_b_submissions_attempted
    fight_stats_dict["fighter_a_reversals"] = fighter_a_reversals
    fight_stats_dict["fighter_b_reversals"] = fighter_b_reversals
    fight_stats_dict["fighter_a_control_time"] = fighter_a_control_time_raw
    fight_stats_dict["fighter_a_control_time_minutes"] = fighter_a_control_time_minutes
    fight_stats_dict["fighter_a_control_time_seconds"] = fighter_a_control_time_seconds
    fight_stats_dict["fighter_b_control_time"] = fighter_b_control_time_raw
    fight_stats_dict["fighter_b_control_time_minutes"] = fighter_b_control_time_minutes
    fight_stats_dict["fighter_b_control_time_seconds"] = fighter_b_control_time_seconds


    return fight_stats_dict