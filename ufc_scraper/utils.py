from collections import defaultdict
from datetime import datetime
import re
from typing import Dict, Iterator, List, Optional, Tuple, Union
from uuid import uuid5, NAMESPACE_URL

from scrapy.http import Response

from entities import Event, Fighter, FightStats


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


def safe_css_get(response: Response, query: str, xpath: Optional[str] = None) -> str:
    """
    Safely extract a single value from a response using a CSS selector,
    optionally refined by an XPath expression.

    Applies the given CSS selector to the response and returns the first
    matching result. If an XPath expression is provided, it is applied
    to the result of the CSS selection before extracting the value.
    Raises a ValueError if no result is found.

    Args:
        response (Response): The response object to query.
        query (str): A CSS selector string.
        xpath (Optional[str]): An optional XPath expression to apply to
            the CSS selection.

    Returns:
        str: The first extracted value matching the selector(s).

    Raises:
        ValueError: If no result is found for the given query (and XPath,
            if provided).
    """
    result: str | None = (
        response.css(query).xpath(xpath).get() if xpath else response.css(query).get()
    )

    if not result:
        raise ValueError(f"No result for query {query} on {response.url}")

    return result


def get_fighter_info(response: Response) -> Fighter:
    url: str = response.url
    id: str = get_uuid_string(url)

    name_query = "span.b-content__title-highlight::text"
    nickname_query = "p.b-content__Nickname::text"
    stats_query = "li.b-list__box-list-item::text"
    record_query = "span.b-content__title-record::text"
    opponents_query = "a.b-link::text"
    opponent_urls_query = "a.b-link::attr(href)"

    name_raw = response.css(name_query).get()
    if name_raw is None:
        raise ValueError(
            f"Fighter name missing from {response.url} with query {name_query}"
        )
    name_clean: str = clean_string(name_raw)
    names: List[str] = name_clean.split(" ")
    full_name = " ".join(names)
    first_name = names[0]
    last_name = " ".join(names[1:])

    nickname_raw = response.css(nickname_query).get()
    nickname = clean_string(nickname_raw) if nickname_raw else ""

    fighter_stats = response.css(stats_query).getall()

    height_raw = fighter_stats[1]
    height_clean = clean_string(height_raw)
    if height_clean == "--":
        height_ft = 0
        height_in = 0
        height_cm = float(0)
    else:
        height_ft = int(height_clean.split("'")[0])
        height_in = int(height_clean.split("'")[1].replace('"', "").strip())
        height_cm = float(((height_ft * 12.0) * 2.54) + (height_in * 2.54))

    weight_raw = fighter_stats[3]
    weight_clean = clean_string(weight_raw).replace("lbs.", "")
    if weight_clean == "--":
        weight_lbs = 0
    else:
        weight_lbs = int(weight_clean)

    reach_raw = fighter_stats[5]
    reach_clean = clean_string(reach_raw).replace('"', "")
    if reach_clean == "--":
        reach_in = 0
        reach_cm = 0
    else:
        reach_in = int(reach_clean)
        reach_cm = int(float(reach_clean) * 2.54)

    stance_raw = fighter_stats[7]
    stance_clean = clean_string(stance_raw)

    dob_raw = fighter_stats[9]
    dob_clean = clean_string(dob_raw)
    if dob_clean == "--":
        dob = ""
    else:
        dob_dt = datetime.strptime(dob_clean, "%b %d, %Y")
        dob = datetime.strftime(dob_dt, "%Y-%m-%d")

    record_raw = response.css(record_query).get()
    if not record_raw:
        raise ValueError(
            f"Fighter record missing from {response.url} with query {record_query}"
        )
    record_clean = clean_string(record_raw)
    record = record_clean.split(": ")[1]
    wins = int(record.split("-")[0])
    losses = int(record.split("-")[1])

    # If a fighter has > 0 no contests, the record looks like 'Record: 28-1-0 (1 NC)'
    try:
        draws = int(record.split("-")[2])
        no_contests = 0
    except ValueError:
        draws = int(record.split("-")[2].split(" ")[0])
        no_contests = int(record.split("-")[2].split(" ")[1].replace("(", ""))

    opponent_text_raw = response.css(opponents_query).getall()
    opponent_text_clean = [clean_string(opponent) for opponent in opponent_text_raw]
    opponent_urls = response.css(opponent_urls_query).getall()
    opponent_text_urls_list = list(zip(opponent_text_clean, opponent_urls))

    text_exclusion_list = [
        ":",
        "ufc",
        "preview",
        "dwcs",
        "vs",
        "strikeforce",
        " - ",
        "pride",
        "dream",
    ]
    opponent_urls_filtered = [
        opponent_url
        for opponent_name, opponent_url in opponent_text_urls_list
        if opponent_url != url
        and all(term not in opponent_name.lower() for term in text_exclusion_list)
    ]
    opponent_id_list = [
        get_uuid_string(opponent_url) for opponent_url in opponent_urls_filtered
    ]
    opponents = ", ".join(opponent_id_list)

    return Fighter(
        fighter_id=id,
        url=url,
        full_name=full_name,
        first_name=first_name,
        last_name=last_name,
        nickname=nickname,
        height_ft=height_ft,
        height_in=height_in,
        height_cm=height_cm,
        weight_lbs=weight_lbs,
        reach_in=reach_in,
        reach_cm=reach_cm,
        stance=stance_clean,
        dob=dob,
        wins=wins,
        losses=losses,
        draws=draws,
        no_contests=no_contests,
        opponents=opponents,
    )


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
