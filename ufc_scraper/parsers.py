from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, List, Optional

from scrapy.http import Response

from constants import WEIGHT_CLASSES_LOWER
from entities import Fight, Fighter
from utils import clean_string, get_uuid_string


class Parser(ABC):
    def __init__(self, response: Response):
        self._response = response
        self._url: str = self._response.url
        self._id: str = get_uuid_string(self._url)

    @abstractmethod
    def parse_response(self) -> Any:
        pass

    def _safe_css_get(self, query: str, xpath: Optional[str] = None) -> str:
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
            self._response.css(query).xpath(xpath).get()
            if xpath
            else self._response.css(query).get()
        )

        if not result:
            raise ValueError(f"No result for query {query} on {self._url}")

        return result


class FightInfoParser(Parser):
    def __init__(self, response: Response):
        super().__init__(response)
        self._fighter_url_query = "a.b-link::attr(href)"
        self._bout_type_query = "i.b-fight-details__fight-title::text"
        self._round_text_query = ".b-fight-details__label:contains('Round:')"
        self._finish_method_query = (
            ".b-fight-details__label:contains('Method:') + i::text"
        )
        self._finish_submethod_query = ".b-fight-details__label:contains('Details:')"
        self._finish_round_query = ".b-fight-details__label:contains('Round:')"
        self._finish_time_query = ".b-fight-details__label:contains('Time:')"
        self._referee_query = (
            ".b-fight-details__label:contains('Referee:') + span::text"
        )
        self._judges_query = "i.b-fight-details__text-item"
        self._next_element_xpath = "./following-sibling::text()"
        self._finish_submethod_xpath = "./ancestor::p/text()[normalize-space()]"
        self._span_text_xpath = "./span/text()"

    def _get_fighter_ids(self) -> None:
        all_urls = self._response.css(self._fighter_url_query).getall()
        fighter_1_url = all_urls[1]
        fighter_2_url = all_urls[2]
        self._fighter_1_id = get_uuid_string(fighter_1_url)
        self._fighter_2_id = get_uuid_string(fighter_2_url)

    def _get_weight_class(self) -> None:
        bout_type_raw = self._safe_css_get(self._bout_type_query)
        bout_type_clean = clean_string(bout_type_raw)
        for weight_class in WEIGHT_CLASSES_LOWER:
            if weight_class in bout_type_clean.lower():
                self._weight_class = weight_class

    def _get_num_rounds(self) -> None:
        num_rounds_raw = self._safe_css_get(
            query=self._round_text_query, xpath=self._next_element_xpath
        )
        self._num_rounds = int(clean_string(num_rounds_raw))

    def _get_finish_method(self) -> None:
        finish_method_raw = self._safe_css_get(self._finish_method_query)
        finish_method_clean = clean_string(finish_method_raw)

        if "decision" in finish_method_clean.lower():
            decision = finish_method_clean.split(" - ")
            self._finish_method = decision[0]
            self._finish_submethod = decision[1]
        else:
            self._finish_method = finish_method_clean
            finish_submethod_raw = self._safe_css_get(
                query=self._finish_submethod_query, xpath=self._finish_submethod_xpath
            )
            self._finish_submethod = clean_string(finish_submethod_raw)

    def _get_finish_round(self) -> None:
        finish_round_raw = self._safe_css_get(
            query=self._finish_round_query, xpath=self._next_element_xpath
        )
        self._finish_round = int(clean_string(finish_round_raw))

        finish_time_raw = self._safe_css_get(
            query=self._finish_time_query, xpath=self._next_element_xpath
        )
        finish_time = clean_string(finish_time_raw).split(":")
        self._finish_time_minute = int(finish_time[0])
        self._finish_time_second = int(finish_time[1])

    def _get_referee(self) -> None:
        referee_raw = self._safe_css_get(
            query=self._finish_round_query, xpath=self._next_element_xpath
        )
        self._referee = clean_string(referee_raw)

    def _get_judges(self) -> None:
        judge_and_referee_list = (
            self._response.css(self._judges_query).xpath(self._span_text_xpath).getall()
        )
        self._judge_1_id = ""
        self._judge_2_id = ""
        self._judge_3_id = ""

        if len(judge_and_referee_list) > 1:
            judge_list = judge_and_referee_list[1:]
            judge_list_clean = [clean_string(judge) for judge in judge_list]
            self._judge_1_id = get_uuid_string(judge_list_clean[0])
            self._judge_2_id = get_uuid_string(judge_list_clean[1])
            self._judge_3_id = get_uuid_string(judge_list_clean[2])

    def parse_response(self) -> Fight:
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
            finish_submethod=self._finish_submethod,
            finish_round=self._finish_round,
            finish_time_minute=self._finish_time_minute,
            finish_time_second=self._finish_time_second,
            referee=self._referee,
            judge_1_id=self._judge_1_id,
            judge_2_id=self._judge_2_id,
            judge_3_id=self._judge_3_id,
        )


class FighterInfoParser(Parser):
    def __init__(self, response: Response):
        super().__init__(response)
        self._name_query = "span.b-content__title-highlight::text"
        self._nickname_query = "p.b-content__Nickname::text"
        self._stats_query = "li.b-list__box-list-item::text"
        self._record_query = "span.b-content__title-record::text"
        self._opponents_query = "a.b-link::text"
        self._opponent_urls_query = "a.b-link::attr(href)"

    def _get_fighter_name(self) -> None:
        name_raw = self._safe_css_get(self._name_query)
        name_clean = clean_string(name_raw)
        names: List[str] = name_clean.split(" ")
        self._full_name = " ".join(names)
        self._first_name = names[0]
        self._last_names = " ".join(names[1:])

        nickname_raw = self._response.css(self._nickname_query).get()
        self._nickname = clean_string(nickname_raw) if nickname_raw else ""

    def _get_fighter_stats(self) -> None:
        fighter_stats = self._response.css(self._stats_query).getall()

        # Set default values
        self._height_ft = None
        self._height_in = None
        self._height_cm = None
        self._weight_lbs = None
        self._reach_in = None
        self._reach_cm = None

        height = clean_string(fighter_stats[1])
        if height != "--":
            self._height_ft = int(height.split("'")[0])
            self._height_in = int(height.split("'")[1].replace('"', "").strip())
            self._height_cm = float(
                ((self._height_ft * 12.0) * 2.54) + (self._height_in * 2.54)
            )

        weight = clean_string(fighter_stats[3]).replace("lbs.", "")
        if weight != "--":
            self._weight_lbs = int(weight)

        reach = clean_string(fighter_stats[5]).replace('"', "")
        if reach != "--":
            self._reach_in = int(reach)
            self._reach_cm = int(float(reach) * 2.54)

        self._stance = clean_string(fighter_stats[7])

        dob_string = clean_string(fighter_stats[9])
        if dob_string != "--":
            dob_dt = datetime.strptime(dob_string, "%b %d, %Y")
            self._dob = datetime.strftime(dob_dt, "%Y-%m-%d")

    def _get_fighter_record(self) -> None:
        record_raw = self._safe_css_get(self._record_query)
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
        opponent_text_raw = self._response.css(self._opponents_query).getall()
        opponent_text_clean = [clean_string(opponent) for opponent in opponent_text_raw]
        opponent_urls = self._response.css(self._opponent_urls_query).getall()
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
        self._get_fighter_name()
        self._get_fighter_stats()
        self._get_fighter_record()
        self._get_opponents()

        return Fighter(
            fighter_id=self._id,
            url=self._url,
            full_name=self._full_name,
            first_name=self._first_name,
            last_names=self._last_names,
            nickname=self._nickname,
            height_ft=self._height_ft,
            height_in=self._height_in,
            height_cm=self._height_cm,
            weight_lbs=self._weight_lbs,
            reach_in=self._reach_in,
            reach_cm=self._reach_cm,
            stance=self._stance,
            dob=self._dob,
            record=self._record,
            wins=self._wins,
            losses=self._losses,
            draws=self._draws,
            no_contests=self._no_contests,
            opponents=self._opponents,
        )
