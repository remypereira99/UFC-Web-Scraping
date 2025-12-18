from collections import defaultdict
from datetime import datetime
import re
from typing import Dict, Generator, List, Tuple, Union
from uuid import uuid5, NAMESPACE_URL

from scrapy.http import Response

from entities import Event, Fight, Fighter, FightStats
from constants import WEIGHT_CLASSES_LOWER


def clean_string(raw_string: str) -> str:
    return re.sub(r"\s+", " ", raw_string).strip()


def get_uuid_string(input_string: str) -> str:
    return str(uuid5(namespace=NAMESPACE_URL, name=input_string))


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


def get_fight_info(response: Response) -> Fight:
    url: str = response.url
    fight_id = get_uuid_string(url)

    fighter_url_query = "a.b-link::attr(href)"
    bout_type_query = "i.b-fight-details__fight-title::text"
    time_format_query = ".b-fight-details__label:contains('Time format:')"
    finish_method_query = ".b-fight-details__label:contains('Method:') + i::text"
    finish_submethod_query = ".b-fight-details__label:contains('Details:')"
    finish_round_query = ".b-fight-details__label:contains('Round:')"
    finish_time_query = ".b-fight-details__label:contains('Time:')"
    referee_query = ".b-fight-details__label:contains('Referee:') + span::text"
    judges_query = "i.b-fight-details__text-item"

    all_parent_text_xpath = "./parent::*/text()"
    finish_submethod_xpath = "./ancestor::p/text()[normalize-space()]"
    judges_xpath = "./span/text()"

    all_urls: List[str] = response.css(fighter_url_query).getall()
    fighter_1_url = all_urls[1]
    fighter_2_url = all_urls[2]
    fighter_1_id = get_uuid_string(fighter_1_url)
    fighter_2_id = get_uuid_string(fighter_2_url)

    bout_type_raw: Union[str, None] = response.css(bout_type_query).get()
    if not bout_type_raw:
        raise ValueError(
            f"Bout type missing from {response.url} with query {bout_type_query}"
        )
    bout_type_clean: str = clean_string(bout_type_raw)
    weight_class: str = (
        bout_type_clean.lower()
        if bout_type_clean.lower() in WEIGHT_CLASSES_LOWER
        else ""
    )

    time_format_raw: str = (
        response.css(time_format_query).xpath(all_parent_text_xpath).getall()[1]
    )
    time_format_clean: str = clean_string(time_format_raw)
    num_rounds = int(time_format_clean.split(" ")[0])

    finish_method_raw: Union[str, None] = response.css(finish_method_query).get()
    if not finish_method_raw:
        raise ValueError(
            f"Finish method missing from {response.url} with query {finish_method_query}"
        )
    finish_method_clean: str = clean_string(finish_method_raw)

    if finish_method_clean.split(" ")[0].lower() == "decision":
        decision: List[str] = finish_method_clean.split(" - ")
        finish_method = decision[0].lower()
        finish_submethod = decision[1].lower()
    else:
        finish_method = finish_method_clean.lower()
        finish_submethod_raw: Union[str, None] = (
            response.css(finish_submethod_query).xpath(finish_submethod_xpath).get()
        )
        if not finish_submethod_raw:
            raise ValueError(
                f"Finish submethod missing from {response.url} with query {finish_submethod_query}"
            )
        finish_submethod = clean_string(finish_submethod_raw)

    finish_round_raw = (
        response.css(finish_round_query).xpath(all_parent_text_xpath).getall()[1]
    )
    finish_round = int(clean_string(finish_round_raw))

    finish_time_raw = (
        response.css(finish_time_query).xpath(all_parent_text_xpath).getall()[1]
    )
    finish_time = clean_string(finish_time_raw)
    finish_time_minute = int(finish_time.split(":")[0])
    finish_time_second = int(finish_time.split(":")[1])

    referee_raw = response.css(referee_query).get()
    if not referee_raw:
        raise ValueError(
            f"Referee missing from {response.url} with query {referee_query}"
        )
    referee = clean_string(referee_raw)

    judges_raw: List[str] = response.css(judges_query).xpath(judges_xpath).getall()[1:]
    judges_clean: List[str] = [clean_string(judge) for judge in judges_raw]
    judge_1_id = get_uuid_string(judges_clean[0])
    judge_2_id = get_uuid_string(judges_clean[1])
    judge_3_id = get_uuid_string(judges_clean[2])

    return Fight(
        fight_id=fight_id,
        url=url,
        fighter_1_id=fighter_1_id,
        fighter_2_id=fighter_2_id,
        weight_class=weight_class,
        num_rounds=num_rounds,
        finish_method=finish_method,
        finish_submethod=finish_submethod,
        finish_round=finish_round,
        finish_time_minute=finish_time_minute,
        finish_time_second=finish_time_second,
        referee=referee,
        judge_1_id=judge_1_id,
        judge_2_id=judge_2_id,
        judge_3_id=judge_3_id,
    )


def get_fight_stats_from_summary(fight_stat_summary: str) -> Tuple[int, int]:
    fight_stat_summary_split: List[str] = clean_string(fight_stat_summary).split(" of ")
    landed = int(fight_stat_summary_split[0])
    attempted = int(fight_stat_summary_split[1])

    return landed, attempted


def get_fight_stats(response: Response) -> Generator[FightStats]:
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

    fighter_a_values = values_clean[0::2]
    fighter_b_values = values_clean[1::2]
    fighter_a_summary_stats_dict = dict(zip(headers_clean, fighter_a_values))
    fighter_b_summary_stats_dict = dict(zip(headers_clean, fighter_b_values))

    for summary_stats_dict in (
        fighter_a_summary_stats_dict,
        fighter_b_summary_stats_dict,
    ):
        (total_strikes_landed, total_strikes_attempted) = get_fight_stats_from_summary(
            summary_stats_dict["Total str."]
        )
        (significant_strikes_landed, significant_strikes_attempted) = (
            get_fight_stats_from_summary(summary_stats_dict["Sig. str."])
        )
        knockdowns = int(summary_stats_dict["KD"])
        (takedowns_landed, takedowns_attempted) = get_fight_stats_from_summary(
            fighter_a_summary_stats_dict["Td"]
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
