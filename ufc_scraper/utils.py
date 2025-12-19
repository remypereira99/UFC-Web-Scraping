from collections import defaultdict
from datetime import datetime
import re
from typing import Dict, Iterator, List, Tuple, Union
from uuid import uuid5, NAMESPACE_URL

from scrapy.http import Response

from entities import Event, FightStats


def clean_string(raw_string: str) -> str:
    """Normalize whitespace in a string.

    Collapses consecutive whitespace characters (spaces, tabs, newlines, etc.)
    into a single space and removes leading and trailing whitespace.

    Args:
        raw_string (str): The input string to clean.

    Returns:
        str: The cleaned string with normalized whitespace.

    """
    return re.sub(r"\s+", " ", raw_string).strip()


def get_uuid_string(input_string: str) -> str:
    """Generate a deterministic UUID string from an input string.

    Uses UUID version 5 (SHA-1 based) with the URL namespace to produce
    a stable, deterministic UUID.

    Args:
        input_string (str): The input string used to generate the UUID.

    Returns:
        str: The generated UUID represented as a string.

    """
    return str(uuid5(namespace=NAMESPACE_URL, name=input_string))


def get_event_info(response: Response) -> Event:
    url: str = response.url
    event_id = get_uuid_string(url)

    event_name_query = "span.b-content__title-highlight::text"
    fight_urls_query = "a.b-flag::attr(href)"

    event_name_raw = response.css(event_name_query).get()
    if not event_name_raw:
        raise ValueError(
            f"Event name missing from {response.url} with query {event_name_query}"
        )
    event_name_clean: str = clean_string(event_name_raw)

    event_date_location: List[str] = response.css(
        "li.b-list__box-list-item::text"
    ).getall()

    event_date_raw: str = event_date_location[1]
    event_date_clean: str = clean_string(event_date_raw)
    event_date_dt: datetime = datetime.strptime(event_date_clean, "%B %d, %Y")
    event_date: str = datetime.strftime(event_date_dt, "%Y-%m-%d")

    event_location_raw: str = event_date_location[3]
    event_location_clean: str = clean_string(event_location_raw)
    event_location_split: List[str] = event_location_clean.split(", ")
    event_city: str
    event_state: str
    event_country: str
    if len(event_location_split) == 3:
        event_city = event_location_split[0]
        event_state = event_location_split[1]
        event_country = event_location_split[2]
    elif len(event_location_split) == 2:
        event_city = event_location_split[0]
        event_state = ""
        event_country = event_location_split[1]
    else:
        event_city = ""
        event_state = ""
        event_country = ""

    name = event_name_clean
    date = event_date
    city = event_city
    state = event_state
    country = event_country

    fight_urls = response.css(fight_urls_query).getall()
    fight_ids = [get_uuid_string(fight_url) for fight_url in fight_urls]
    fights = ", ".join(fight_ids)

    return Event(
        event_id=event_id,
        url=url,
        name=name,
        date=date,
        city=city,
        state=state,
        country=country,
        fights=fights,
    )


def get_judges_decisions(response: Response) -> Dict[str, Union[str, int]]:
    judge_decision_dict: defaultdict[str, Union[str, int]] = defaultdict()

    judges_raw: List[str] = (
        response.css("i.b-fight-details__text-item").xpath("./span/text()").getall()[1:]
    )
    judges_clean: List[str] = [clean_string(judge) for judge in judges_raw]
    judge_decision_dict["judge_a"] = judges_clean[0]
    judge_decision_dict["judge_b"] = judges_clean[1]
    judge_decision_dict["judge_c"] = judges_clean[2]

    score_regex = r"\d{2} - \d{2}\."
    scores_raw: List[str] = response.css("i.b-fight-details__text-item::text").getall()
    scores_clean: List[str] = [
        clean_string(score).replace(".", "")
        for score in scores_raw
        if re.search(score_regex, score)
    ]
    judge_a_score, judge_b_score, judge_c_score = scores_clean
    judge_scores = zip(
        ["judge_a", "judge_b", "judge_c"], [judge_a_score, judge_b_score, judge_c_score]
    )
    for judge, score in judge_scores:
        judge_decision_dict[f"{judge}_fighter_1_score"] = int(score.split(" - ")[0])
        judge_decision_dict[f"{judge}_fighter_2_score"] = int(score.split(" - ")[1])

    return judge_decision_dict


def get_fight_stats_from_summary(fight_stat_summary: str) -> Tuple[int, int]:
    fight_stat_summary_split: List[str] = clean_string(fight_stat_summary).split(" of ")
    landed = int(fight_stat_summary_split[0])
    attempted = int(fight_stat_summary_split[1])

    return landed, attempted


def get_fight_stats(response: Response) -> Iterator[FightStats]:
    fighter_url_query = "a.b-link::attr(href)"

    url: str = response.url
    fight_id = get_uuid_string(url)
    all_urls: List[str] = response.css(fighter_url_query).getall()
    fighter_1_url = all_urls[1]
    fighter_2_url = all_urls[2]
    fighter_1_id = get_uuid_string(fighter_1_url)
    fighter_2_id = get_uuid_string(fighter_2_url)

    headers_query = (
        "thead.b-fight-details__table-head th.b-fight-details__table-col::text"
    )
    rows_query = "tbody.b-fight-details__table-body tr.b-fight-details__table-row"
    values_query = "p.b-fight-details__table-text::text"

    headers = response.css(headers_query).getall()
    headers_clean = [clean_string(header) for header in headers[1:]]

    rows = response.css(rows_query)
    summary_stats = rows[0]

    values = summary_stats.css(values_query).getall()
    values_clean = [clean_string(value) for value in values[4:]]

    fighter_1_values = values_clean[0::2]
    fighter_2_values = values_clean[1::2]
    fighter_1_summary_stats_dict = dict(zip(headers_clean, fighter_1_values))
    fighter_2_summary_stats_dict = dict(zip(headers_clean, fighter_2_values))
    fighter_1_summary_stats_dict["fighter_id"] = fighter_1_id
    fighter_2_summary_stats_dict["fighter_id"] = fighter_2_id

    for summary_stats_dict in (
        fighter_1_summary_stats_dict,
        fighter_2_summary_stats_dict,
    ):
        fighter_id = summary_stats_dict["fighter_id"]
        fight_stat_id = get_uuid_string(fight_id + fighter_id)
        (total_strikes_landed, total_strikes_attempted) = get_fight_stats_from_summary(
            summary_stats_dict["Total str."]
        )
        (significant_strikes_landed, significant_strikes_attempted) = (
            get_fight_stats_from_summary(summary_stats_dict["Sig. str."])
        )
        knockdowns = int(summary_stats_dict["KD"])
        (takedowns_landed, takedowns_attempted) = get_fight_stats_from_summary(
            summary_stats_dict["Td"]
        )
        control_time_raw = clean_string(summary_stats_dict["Ctrl"])
        (control_time_minutes_string, control_time_seconds_string) = (
            control_time_raw.split(":")
        )
        control_time_minutes = int(control_time_minutes_string)
        control_time_seconds = int(control_time_seconds_string)
        submissions_attempted = int(summary_stats_dict["Sub. att"])
        reversals = int(summary_stats_dict["Rev."])

        yield FightStats(
            fight_stat_id=fight_stat_id,
            fight_id=fight_id,
            fighter_id=fighter_id,
            total_strikes_landed=total_strikes_landed,
            total_strikes_attempted=total_strikes_attempted,
            significant_strikes_landed=significant_strikes_landed,
            significant_strikes_attempted=significant_strikes_attempted,
            knockdowns=knockdowns,
            takedowns_landed=takedowns_landed,
            takedowns_attempted=takedowns_attempted,
            control_time_minutes=control_time_minutes,
            control_time_seconds=control_time_seconds,
            submissions_attempted=submissions_attempted,
            reversals=reversals,
        )
