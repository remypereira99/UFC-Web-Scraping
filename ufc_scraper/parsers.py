"""HTML parsers for UFCStats pages.

This module contains Scrapy-based parsers for UFC events, fights,
fighters, and fight statistics (total and by-round).
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional

from scrapy.http import Response

from constants import (
    WEIGHT_CLASSES_LOWER,
    HREF_QUERY,
    TOTALS_STATS_EXPECTED_HEADERS,
    SIGNIFICANT_STRIKES_EXPECTED_HEADERS,
)
from entities import Event, Fight, Fighter, FightStats, FightStatsByRound
from utils import clean_string, get_uuid_string, get_strikes_landed_attempted


class _Parser(ABC):
    def __init__(self, response: Response):
        self._response = response
        self._url = self._response.url
        self._id = get_uuid_string(self._url)

    @abstractmethod
    def parse_response(self) -> Any:
        pass

    def _safe_css_get(self, query: str, xpath: Optional[str] = None) -> str:
        """Safely extract a single value from a response using a CSS selector.

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
            self._response.css(query).xpath(xpath).get()
            if xpath
            else self._response.css(query).get()
        )

        if not result:
            raise ValueError(f"No result for query {query} on {self._url}")

        return result

    def _safe_css_get_all(self, query: str, xpath: Optional[str] = None) -> List[str]:
        """Safely extract a list of values from a response using a CSS selector.

        Applies the given CSS selector to the response and returns all matching
        results. If an XPath expression is provided, it is applied to the result
        of the CSS selection before extracting the values
        Raises a ValueError if no results are found.

        Args:
            response (Response): The response object to query.
            query (str): A CSS selector string.
            xpath (Optional[str]): An optional XPath expression to apply to
                the CSS selection.

        Returns:
            List[str]: List of all extracted values matching the selector(s).

        Raises:
            ValueError: If no result is found for the given query (and XPath,
                if provided).

        """
        result: List[str] = (
            self._response.css(query).xpath(xpath).getall()
            if xpath
            else self._response.css(query).getall()
        )

        if not result:
            raise ValueError(f"No results for query {query} on {self._url}")

        return result


class FightInfoParser(_Parser):
    """Parses HTTP responses of ufcstats.com fight pages.

    Parses key attributes of UFC fights and yields Fight dataclass.

    Args:
        response (Response): The HTTP response to be parsed.

    Attributes:
        _response (Response): The raw response object.
        _url (str): URL of the response.
        _id (str): Deterministic UUID derived from the response URL.
        _css_queries (Dict[str, str]): Mapping of semantic query names to
            CSS selectors used to extract fight metadata from the response.
        _xpath_queries (Dict[str, str]): Mapping of semantic query names to
            XPath expressions used to refine or post-process CSS selections.

    """

    def __init__(self, response: Response):
        super().__init__(response)
        self._css_queries: Dict[str, str] = {
            "href_query": HREF_QUERY,
            "bout_type_query": "i.b-fight-details__fight-title::text",
            "round_text_query": ".b-fight-details__label:contains('Round:')",
            "finish_method_query": (
                ".b-fight-details__label:contains('Method:') + i::text"
            ),
            "secondary_finish_method_query": ".b-fight-details__label:contains('Details:')",
            "finish_round_query": ".b-fight-details__label:contains('Round:')",
            "finish_time_query": ".b-fight-details__label:contains('Time:')",
            "referee_query": (
                ".b-fight-details__label:contains('Referee:') + span::text"
            ),
            "judges_query": "i.b-fight-details__text-item",
        }
        self._xpath_queries: Dict[str, str] = {
            "next_element_xpath": "./following-sibling::text()",
            "secondary_finish_method_xpath": "./ancestor::p/text()[normalize-space()]",
            "span_text_xpath": "./span/text()",
        }

    def _get_fighter_ids(self) -> None:
        all_urls = self._safe_css_get_all(self._css_queries["href_query"])
        fighter_urls = [url for url in all_urls if "fighter-details" in url]
        fighter_1_url = fighter_urls[0]
        fighter_2_url = fighter_urls[1]
        self._fighter_1_id = get_uuid_string(fighter_1_url)
        self._fighter_2_id = get_uuid_string(fighter_2_url)

    def _get_weight_class(self) -> None:
        bout_type_raw = self._safe_css_get(self._css_queries["bout_type_query"])
        bout_type_clean = clean_string(bout_type_raw)
        for weight_class in WEIGHT_CLASSES_LOWER:
            if weight_class in bout_type_clean.lower():
                self._weight_class = weight_class

    def _get_num_rounds(self) -> None:
        num_rounds_raw = self._safe_css_get(
            query=self._css_queries["round_text_query"],
            xpath=self._xpath_queries["next_element_xpath"],
        )
        self._num_rounds = int(clean_string(num_rounds_raw))

    def _get_finish_method(self) -> None:
        finish_method_raw = self._safe_css_get(self._css_queries["finish_method_query"])
        finish_method_clean = clean_string(finish_method_raw)
        self._finish_method = finish_method_clean

        if "decision" in finish_method_clean.lower():
            decision = finish_method_clean.split(" - ")
            self._primary_finish_method = decision[0].lower()
            self._secondary_finish_method = decision[1].lower()
        else:
            self._primary_finish_method = finish_method_clean.lower()
            secondary_finish_method_raw = self._safe_css_get(
                query=self._css_queries["secondary_finish_method_query"],
                xpath=self._xpath_queries["secondary_finish_method_xpath"],
            )
            self._secondary_finish_method = clean_string(
                secondary_finish_method_raw
            ).lower()

    def _get_finish_round(self) -> None:
        finish_round_raw = self._safe_css_get(
            query=self._css_queries["finish_round_query"],
            xpath=self._xpath_queries["next_element_xpath"],
        )
        self._finish_round = int(clean_string(finish_round_raw))

        finish_time_raw = self._safe_css_get(
            query=self._css_queries["finish_time_query"],
            xpath=self._xpath_queries["next_element_xpath"],
        )
        finish_time = clean_string(finish_time_raw).split(":")
        self._finish_time_minute = int(finish_time[0])
        self._finish_time_second = int(finish_time[1])

    def _get_referee(self) -> None:
        referee_raw = self._safe_css_get(self._css_queries["referee_query"])
        self._referee = clean_string(referee_raw)

    def _get_judges(self) -> None:
        judge_and_referee_list = self._safe_css_get_all(
            query=self._css_queries["judges_query"],
            xpath=self._xpath_queries["span_text_xpath"],
        )
        self._judge_1_id = ""
        self._judge_2_id = ""
        self._judge_3_id = ""

        if len(judge_and_referee_list) > 1:
            judge_list = judge_and_referee_list[1:]
            judge_list_clean = [clean_string(judge) for judge in judge_list]
            self._judge_1 = judge_list_clean[0]
            self._judge_2 = judge_list_clean[1]
            self._judge_3 = judge_list_clean[2]

    def parse_response(self) -> Fight:
        """Parse the HTML response to get key fight attributes.

        Args:
            response (Response): The response object to query.

        Returns:
            Fight: Dataclass containing all key fight attributes.

        """
        self._get_fighter_ids()
        self._get_weight_class()
        self._get_num_rounds()
        self._get_finish_method()
        self._get_finish_round()
        self._get_referee()
        self._get_judges()

        return Fight(
            fight_id=self._id,
            url=self._url,
            fighter_1_id=self._fighter_1_id,
            fighter_2_id=self._fighter_2_id,
            weight_class=self._weight_class,
            num_rounds=self._num_rounds,
            finish_method=self._finish_method,
            primary_finish_method=self._primary_finish_method,
            secondary_finish_method=self._secondary_finish_method,
            finish_round=self._finish_round,
            finish_time_minute=self._finish_time_minute,
            finish_time_second=self._finish_time_second,
            referee=self._referee,
            judge_1=self._judge_1,
            judge_2=self._judge_2,
            judge_3=self._judge_3,
        )


class FighterInfoParser(_Parser):
    """Parses HTTP responses of ufcstats.com fighter pages.

    Parses key attributes of UFC fighters and yields Fighter dataclass.

    Args:
        response (Response): The HTTP response to be parsed.

    Attributes:
        _response (Response): The raw response object.
        _url (str): URL of the response.
        _id (str): Deterministic UUID derived from the response URL.
        _css_queries (Dict[str, str]): Mapping of semantic query names to
            CSS selectors used to extract fight metadata from the response.

    """

    def __init__(self, response: Response):
        super().__init__(response)
        self._css_queries: Dict[str, str] = {
            "href_query": HREF_QUERY,
            "name_query": "span.b-content__title-highlight::text",
            "nickname_query": "p.b-content__Nickname::text",
            "stats_query": "li.b-list__box-list-item::text",
            "record_query": "span.b-content__title-record::text",
            "opponents_query": "a.b-link::text",
        }
        self._fighter_stats = self._safe_css_get_all(self._css_queries["stats_query"])

    def _get_fighter_name(self) -> None:
        name_raw = self._safe_css_get(self._css_queries["name_query"])
        name_clean = clean_string(name_raw)
        names = name_clean.split(" ")
        self._full_name = " ".join(names)
        self._first_name = names[0]
        self._last_names = " ".join(names[1:])

        nickname_raw = self._response.css(self._css_queries["nickname_query"]).get()
        self._nickname = clean_string(nickname_raw) if nickname_raw else ""

    def _get_fighter_height(self) -> None:
        height = clean_string(self._fighter_stats[1])
        if height != "--":
            self._height_ft = int(height.split("'")[0])
            self._height_in = int(height.split("'")[1].replace('"', "").strip())
            self._height_cm = float(
                ((self._height_ft * 12.0) * 2.54) + (self._height_in * 2.54)
            )

    def _get_fighter_weight(self) -> None:
        weight = clean_string(self._fighter_stats[3]).replace("lbs.", "")
        if weight != "--":
            self._weight_lbs = int(weight)

    def _get_fighter_reach(self) -> None:
        reach = clean_string(self._fighter_stats[5]).replace('"', "")
        if reach != "--":
            self._reach_in = int(reach)
            self._reach_cm = int(float(reach) * 2.54)

    def _get_fighter_stance(self) -> None:
        self._stance = clean_string(self._fighter_stats[7])

    def _get_fighter_dob(self) -> None:
        dob_string = clean_string(self._fighter_stats[9])
        if dob_string != "--":
            dob_dt = datetime.strptime(dob_string, "%b %d, %Y")
            self._dob = datetime.strftime(dob_dt, "%Y-%m-%d")

    def _get_fighter_record(self) -> None:
        record_raw = self._safe_css_get(self._css_queries["record_query"])
        record_clean = clean_string(record_raw)
        self._record = record_clean.split(": ")[1]
        self._wins = int(self._record.split("-")[0])
        self._losses = int(self._record.split("-")[1])

        # If a fighter has > 0 no contests, the record looks like 'Record: 28-1-0 (1 NC)'
        try:
            self._draws = int(self._record.split("-")[2])
            self._no_contests = 0
        except ValueError:
            self._draws = int(self._record.split("-")[2].split(" ")[0])
            self._no_contests = int(
                self._record.split("-")[2].split(" ")[1].replace("(", "")
            )

    def _get_opponents(self) -> None:
        opponent_text_raw = self._safe_css_get_all(self._css_queries["opponents_query"])
        opponent_text_clean = [clean_string(opponent) for opponent in opponent_text_raw]
        opponent_urls = self._safe_css_get_all(self._css_queries["href_query"])
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
            if opponent_url != self._url
            and all(term not in opponent_name.lower() for term in text_exclusion_list)
        ]
        opponent_id_list = [
            get_uuid_string(opponent_url) for opponent_url in opponent_urls_filtered
        ]

        self._opponents = ", ".join(opponent_id_list)

    def parse_response(self) -> Fighter:
        """Parse the HTML response to get key fighter attributes.

        Args:
            response (Response): The response object to query.

        Returns:
            Fighter: Dataclass containing all key fighter attributes.

        """
        self._get_fighter_name()
        self._get_fighter_height()
        self._get_fighter_weight()
        self._get_fighter_reach()
        self._get_fighter_stance()
        self._get_fighter_dob()
        self._get_fighter_record()
        self._get_opponents()

        return Fighter(
            fighter_id=self._id,
            url=self._url,
            full_name=self._full_name,
            first_name=self._first_name,
            last_names=self._last_names,
            nickname=self._nickname,
            height_ft=self._height_ft if self._height_ft else None,
            height_in=self._height_in if self._height_in else None,
            height_cm=self._height_cm if self._height_cm else None,
            weight_lbs=self._weight_lbs if self._weight_lbs else None,
            reach_in=self._reach_in if self._reach_in else None,
            reach_cm=self._reach_cm if self._reach_cm else None,
            stance=self._stance,
            dob=self._dob,
            record=self._record,
            wins=self._wins,
            losses=self._losses,
            draws=self._draws,
            no_contests=self._no_contests,
            opponents=self._opponents,
        )


class EventInfoParser(_Parser):
    """Parses HTTP responses of ufcstats.com event pages.

    Parses key attributes of UFC events and yields Event dataclass.

    Args:
        response (Response): The HTTP response to be parsed.

    Attributes:
        _response (Response): The raw response object.
        _url (str): URL of the response.
        _id (str): Deterministic UUID derived from the response URL.
        _css_queries (Dict[str, str]): Mapping of semantic query names to
            CSS selectors used to extract fight metadata from the response.

    """

    def __init__(self, response: Response):
        super().__init__(response)
        self._css_queries: Dict[str, str] = {
            "event_name_query": "span.b-content__title-highlight::text",
            "fight_urls_query": "a.b-flag::attr(href)",
        }
        self._event_date_location = self._safe_css_get_all(
            "li.b-list__box-list-item::text"
        )

    def _get_event_name(self) -> None:
        event_name_raw = self._safe_css_get(self._css_queries["event_name_query"])
        self._name = clean_string(event_name_raw)

    def _get_event_date(self) -> None:
        event_date_raw = self._event_date_location[1]
        self._event_date = clean_string(event_date_raw)
        event_date_dt = datetime.strptime(self._event_date, "%B %d, %Y")
        self._event_date_formatted = datetime.strftime(event_date_dt, "%Y-%m-%d")

    def _get_event_location(self) -> None:
        event_location_raw: str = self._event_date_location[3]
        event_location_clean: str = clean_string(event_location_raw)
        event_location_split = event_location_clean.split(", ")

        self._city = ""
        self._state = ""
        self._country = ""
        if len(event_location_split) == 3:
            self._city = event_location_split[0]
            self._state = event_location_split[1]
            self._country = event_location_split[2]
        elif len(event_location_split) == 2:
            self._city = event_location_split[0]
            self._country = event_location_split[1]

    def _get_fights(self) -> None:
        fight_urls = self._safe_css_get_all(self._css_queries["fight_urls_query"])
        fight_ids = [get_uuid_string(fight_url) for fight_url in fight_urls]
        self._fights = ", ".join(fight_ids)

    def parse_response(self) -> Event:
        """Parse the HTML response to get key event attributes.

        Args:
            response (Response): The response object to query.

        Returns:
            Event: Dataclass containing all key event attributes.

        """
        return Event(
            event_id=self._id,
            url=self._url,
            name=self._name,
            date=self._event_date,
            date_formatted=self._event_date_formatted,
            city=self._city,
            state=self._state,
            country=self._country,
            fights=self._fights,
        )


class FightStatParser(_Parser):
    """Parses HTTP responses of ufcstats.com fight pages.

    Parses fight statistics from UFC fights and yields a FightStats dataclass
    for each fighter.

    Args:
        response (Response): The HTTP response to be parsed.

    Attributes:
        _response (Response): The raw response object.
        _url (str): URL of the response.
        _id (str): Deterministic UUID derived from the response URL.
        _css_queries (Dict[str, str]): Mapping of semantic query names to
            CSS selectors used to extract fight metadata from the response.

    """

    def __init__(self, response: Response):
        super().__init__(response)
        self._css_queries: Dict[str, str] = {
            "fighter_urls_query": "a.b-link.b-fight-details__person-link::attr(href)",
            "headers_query": (
                "thead.b-fight-details__table-head th.b-fight-details__table-col::text"
            ),
            "round_headers_query": (
                "thead.b-fight-details__table-row  th.b-fight-details__table-col::text"
            ),
            "stat_values_query": (
                "tbody.b-fight-details__table-body p.b-fight-details__table-text::text"
            ),
            "rows_query": (
                "tbody.b-fight-details__table-body tr.b-fight-details__table-row"
            ),
            "values_query": "p.b-fight-details__table-text::text",
        }
        self._fight_id = self._id
        self._get_fighter_ids()

    def _get_fighter_ids(self) -> None:
        fighter_urls = tuple(
            self._safe_css_get_all(self._css_queries["fighter_urls_query"])
        )
        fighter_1_url, fighter_2_url = fighter_urls
        self._fighter_1_id = get_uuid_string(fighter_1_url)
        self._fighter_2_id = get_uuid_string(fighter_2_url)

    def _get_fight_stat_headers(self) -> None:
        headers = self._safe_css_get_all(self._css_queries["headers_query"])
        headers_clean = [clean_string(header) for header in headers]

        round_headers = self._safe_css_get_all(self._css_queries["round_headers_query"])
        round_headers_clean = [
            clean_string(round_header) for round_header in round_headers
        ]
        # Divide by two as the number of rounds is duplicated for stats and significant strikes
        self._num_rounds = int(len(round_headers_clean) / 2)

        totals_headers_clean = headers_clean[0:10]
        totals_headers_clean.remove("Fighter")
        assert totals_headers_clean == TOTALS_STATS_EXPECTED_HEADERS, (
            f"Totals headers {totals_headers_clean} for url {self._url}",
            f"do not match expected headers: {TOTALS_STATS_EXPECTED_HEADERS}",
        )
        totals_by_round_headers = [
            f"{header}_round_{round}"
            for round in range(1, self._num_rounds + 1)
            for header in totals_headers_clean
        ]

        sig_strikes_headers_clean = headers_clean[10:]
        sig_strikes_headers_clean.remove("Fighter")
        assert sig_strikes_headers_clean == SIGNIFICANT_STRIKES_EXPECTED_HEADERS, (
            f"Totals headers {sig_strikes_headers_clean} for url {self._url}",
            f"do not match expected headers: {SIGNIFICANT_STRIKES_EXPECTED_HEADERS}",
        )
        sig_strikes_by_round_headers = [
            f"{header}_round_{round}"
            for round in range(1, self._num_rounds + 1)
            for header in sig_strikes_headers_clean
        ]

        self._all_stat_headers = (
            totals_headers_clean
            + totals_by_round_headers
            + sig_strikes_headers_clean
            + sig_strikes_by_round_headers
        )

    def _get_fight_stat_values(self) -> None:
        values = self._safe_css_get_all(self._css_queries["stat_values_query"])
        values_clean = [
            clean_string(value) for value in values if clean_string(value) != ""
        ]

        self._fighter_1_stat_values = values_clean[0::2]
        self._fighter_2_stat_values = values_clean[1::2]

    def _get_fight_stat_dicts(self) -> None:
        self._get_fight_stat_headers()
        self._get_fight_stat_values()

        num_fighter_1_values = len(self._fighter_1_stat_values)
        num_fighter_2_values = len(self._fighter_2_stat_values)
        num_headers = len(self._all_stat_headers)
        assert num_fighter_1_values == num_headers, (
            f"Number of stat values {num_fighter_1_values} does not match number of",
            f"headers {num_headers} for fighter_1: {self._fighter_1_id}",
        )
        assert num_fighter_2_values == num_headers, (
            f"Number of stat values {num_fighter_2_values} does not match number of",
            f"headers {num_headers} for fighter_1: {self._fighter_2_id}",
        )

        fighter_1_stats_dict = dict(
            zip(self._all_stat_headers, self._fighter_1_stat_values)
        )
        fighter_2_stats_dict = dict(
            zip(self._all_stat_headers, self._fighter_2_stat_values)
        )
        self._fighter_stats_dicts = {
            self._fighter_1_id: fighter_1_stats_dict,
            self._fighter_2_id: fighter_2_stats_dict,
        }

    def _get_fight_stats(self, fighter_id: str) -> FightStats:
        self._get_fight_stat_dicts()
        fighter_stat_dict = self._fighter_stats_dicts[fighter_id]

        fight_stat_id = get_uuid_string(self._fight_id + fighter_id)
        (total_strikes_landed, total_strikes_attempted) = get_strikes_landed_attempted(
            fighter_stat_dict["Total str."]
        )
        (significant_strikes_landed, significant_strikes_attempted) = (
            get_strikes_landed_attempted(fighter_stat_dict["Sig. str."])
        )
        (significant_strikes_landed_head, significant_strikes_attempted_head) = (
            get_strikes_landed_attempted(fighter_stat_dict["Head"])
        )
        (significant_strikes_landed_body, significant_strikes_attempted_body) = (
            get_strikes_landed_attempted(fighter_stat_dict["Body"])
        )
        (significant_strikes_landed_leg, significant_strikes_attempted_leg) = (
            get_strikes_landed_attempted(fighter_stat_dict["Leg"])
        )
        (
            significant_strikes_landed_distance,
            significant_strikes_attempted_distance,
        ) = get_strikes_landed_attempted(fighter_stat_dict["Distance"])
        (significant_strikes_landed_clinch, significant_strikes_attempted_clinch) = (
            get_strikes_landed_attempted(fighter_stat_dict["Clinch"])
        )
        (significant_strikes_landed_ground, significant_strikes_attempted_ground) = (
            get_strikes_landed_attempted(fighter_stat_dict["Ground"])
        )
        knockdowns = int(fighter_stat_dict["KD"])
        (takedowns_landed, takedowns_attempted) = get_strikes_landed_attempted(
            fighter_stat_dict["Td"]
        )
        control_time_raw = clean_string(fighter_stat_dict["Ctrl"])
        (control_time_minutes_string, control_time_seconds_string) = (
            control_time_raw.split(":")
        )
        control_time_minutes = int(control_time_minutes_string)
        control_time_seconds = int(control_time_seconds_string)
        submissions_attempted = int(fighter_stat_dict["Sub. att"])
        reversals = int(fighter_stat_dict["Rev."])

        return FightStats(
            fight_stat_id=fight_stat_id,
            fight_id=self._fight_id,
            fighter_id=fighter_id,
            total_strikes_landed=total_strikes_landed,
            total_strikes_attempted=total_strikes_attempted,
            significant_strikes_landed=significant_strikes_landed,
            significant_strikes_attempted=significant_strikes_attempted,
            significant_strikes_landed_head=significant_strikes_landed_head,
            significant_strikes_attempted_head=significant_strikes_attempted_head,
            significant_strikes_landed_body=significant_strikes_landed_body,
            significant_strikes_attempted_body=significant_strikes_attempted_body,
            significant_strikes_landed_leg=significant_strikes_landed_leg,
            significant_strikes_attempted_leg=significant_strikes_attempted_leg,
            significant_strikes_landed_distance=significant_strikes_landed_distance,
            significant_strikes_attempted_distance=significant_strikes_attempted_distance,
            significant_strikes_landed_clinch=significant_strikes_landed_clinch,
            significant_strikes_attempted_clinch=significant_strikes_attempted_clinch,
            significant_strikes_landed_ground=significant_strikes_landed_ground,
            significant_strikes_attempted_ground=significant_strikes_attempted_ground,
            knockdowns=knockdowns,
            takedowns_landed=takedowns_landed,
            takedowns_attempted=takedowns_attempted,
            control_time_minutes=control_time_minutes,
            control_time_seconds=control_time_seconds,
            submissions_attempted=submissions_attempted,
            reversals=reversals,
        )

    def parse_response(self) -> Iterator[Any]:
        """Parse the HTML response to get key fight stats.

        Args:
            response (Response): The response object to query.

        Returns:
            Iterator[FightStats]: Dataclass containing all key fight stats attributes.
                Yields one FightStats object per fighter.

        """
        fighter_1_stats = self._get_fight_stats(self._fighter_1_id)
        fighter_2_stats = self._get_fight_stats(self._fighter_2_id)

        yield fighter_1_stats
        yield fighter_2_stats


class FightStatByRoundParser(FightStatParser):
    """Parses HTTP responses of ufcstats.com fight pages.

    Parses fight statistics from each round of UFC fights and yields a FightStatsByRound
    dataclass per fighter per round.

    Args:
        response (Response): The HTTP response to be parsed.

    Attributes:
        _response (Response): The raw response object.
        _url (str): URL of the response.
        _id (str): Deterministic UUID derived from the response URL.

    """

    def __init__(self, response: Response):
        super().__init__(response)

    def _get_fight_stats_by_round(
        self, fighter_id: str, round: int
    ) -> FightStatsByRound:
        fighter_stat_dict = self._fighter_stats_dicts[fighter_id]
        fight_stat_by_round_id = get_uuid_string(
            self._fight_id + fighter_id + str(round)
        )

        (total_strikes_landed, total_strikes_attempted) = get_strikes_landed_attempted(
            fighter_stat_dict[f"Total str._round_{round}"]
        )
        (significant_strikes_landed, significant_strikes_attempted) = (
            get_strikes_landed_attempted(fighter_stat_dict[f"Sig. str._round_{round}"])
        )
        (significant_strikes_landed_head, significant_strikes_attempted_head) = (
            get_strikes_landed_attempted(fighter_stat_dict[f"Head_round_{round}"])
        )
        (significant_strikes_landed_body, significant_strikes_attempted_body) = (
            get_strikes_landed_attempted(fighter_stat_dict[f"Body_round_{round}"])
        )
        (significant_strikes_landed_leg, significant_strikes_attempted_leg) = (
            get_strikes_landed_attempted(fighter_stat_dict[f"Leg_round_{round}"])
        )
        (
            significant_strikes_landed_distance,
            significant_strikes_attempted_distance,
        ) = get_strikes_landed_attempted(fighter_stat_dict[f"Distance_round_{round}"])
        (significant_strikes_landed_clinch, significant_strikes_attempted_clinch) = (
            get_strikes_landed_attempted(fighter_stat_dict[f"Clinch_round_{round}"])
        )
        (significant_strikes_landed_ground, significant_strikes_attempted_ground) = (
            get_strikes_landed_attempted(fighter_stat_dict[f"Ground_round_{round}"])
        )
        knockdowns = int(fighter_stat_dict[f"KD_round_{round}"])
        (takedowns_landed, takedowns_attempted) = get_strikes_landed_attempted(
            fighter_stat_dict[f"Td_round_{round}"]
        )
        control_time_raw = clean_string(fighter_stat_dict[f"Ctrl_round_{round}"])
        (control_time_minutes_string, control_time_seconds_string) = (
            control_time_raw.split(":")
        )
        control_time_minutes = int(control_time_minutes_string)
        control_time_seconds = int(control_time_seconds_string)
        submissions_attempted = int(fighter_stat_dict[f"Sub. att_round_{round}"])
        reversals = int(fighter_stat_dict[f"Rev._round_{round}"])

        return FightStatsByRound(
            fight_stat_by_round_id=fight_stat_by_round_id,
            fight_id=self._fight_id,
            fighter_id=fighter_id,
            round=round,
            total_strikes_landed=total_strikes_landed,
            total_strikes_attempted=total_strikes_attempted,
            significant_strikes_landed=significant_strikes_landed,
            significant_strikes_attempted=significant_strikes_attempted,
            significant_strikes_landed_head=significant_strikes_landed_head,
            significant_strikes_attempted_head=significant_strikes_attempted_head,
            significant_strikes_landed_body=significant_strikes_landed_body,
            significant_strikes_attempted_body=significant_strikes_attempted_body,
            significant_strikes_landed_leg=significant_strikes_landed_leg,
            significant_strikes_attempted_leg=significant_strikes_attempted_leg,
            significant_strikes_landed_distance=significant_strikes_landed_distance,
            significant_strikes_attempted_distance=significant_strikes_attempted_distance,
            significant_strikes_landed_clinch=significant_strikes_landed_clinch,
            significant_strikes_attempted_clinch=significant_strikes_attempted_clinch,
            significant_strikes_landed_ground=significant_strikes_landed_ground,
            significant_strikes_attempted_ground=significant_strikes_attempted_ground,
            knockdowns=knockdowns,
            takedowns_landed=takedowns_landed,
            takedowns_attempted=takedowns_attempted,
            control_time_minutes=control_time_minutes,
            control_time_seconds=control_time_seconds,
            submissions_attempted=submissions_attempted,
            reversals=reversals,
        )

    def parse_response(self) -> Iterator[Any]:
        """Parse the HTML response to get key fight stats per round.

        Args:
            response (Response): The response object to query.

        Returns:
            Iterator[FightStatsByRound]: Dataclass containing all key fight stats attributes.
                Yields one FightStatsByRound object per fighter per round.

        """
        self._get_fight_stat_dicts()

        for round in range(1, self._num_rounds + 1):
            fighter_1_by_round_stats = self._get_fight_stats_by_round(
                fighter_id=self._fighter_1_id, round=round
            )
            fighter_2_by_round_stats = self._get_fight_stats_by_round(
                fighter_id=self._fighter_2_id, round=round
            )

            yield fighter_1_by_round_stats
            yield fighter_2_by_round_stats
