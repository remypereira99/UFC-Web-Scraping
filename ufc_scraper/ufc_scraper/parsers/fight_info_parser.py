"""HTML parsers for UFCStats pages.

This module contains Scrapy-based parsers for UFC events, fights,
fighters, and fight statistics (total and by-round).
"""

from datetime import datetime, timezone

from scrapy.http import Response

from . import WEIGHT_CLASSES_LOWER
from base_parser import Parser
from entities import Fight
from utils import (
    clean_string,
    get_uuid_string,
)


class FightInfoParser(Parser):
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

    """

    def __init__(self, response: Response):
        super().__init__(response)

    def _get_event_id(self) -> None:
        event_url = self._safe_css_get(self._css_queries.event_urls_query)
        self._event_id = get_uuid_string(event_url)

    def _get_fighter_ids(self) -> None:
        all_urls = self._safe_css_get_all(self._css_queries.href_query)
        fighter_urls = [url for url in all_urls if "fighter-details" in url]
        fighter_1_url = fighter_urls[0]
        fighter_2_url = fighter_urls[1]
        self._fighter_1_id = get_uuid_string(fighter_1_url)
        self._fighter_2_id = get_uuid_string(fighter_2_url)

    def _get_weight_class(self) -> None:
        bout_type_text = self._safe_css_get_all(self._css_queries.bout_type_query)
        bout_type = [
            clean_string(text) for text in bout_type_text if clean_string(text) != ""
        ][0]
        self._weight_class = None
        for weight_class in WEIGHT_CLASSES_LOWER:
            if weight_class in bout_type.lower():
                self._weight_class = weight_class

    def _get_num_rounds(self) -> None:
        num_rounds_raw = self._safe_css_get(
            query=self._css_queries.round_text_query,
            xpath=self._css_queries.next_element_xpath,
        )
        self._num_rounds = int(clean_string(num_rounds_raw))

    def _get_finish_method(self) -> None:
        finish_method_raw = self._safe_css_get(self._css_queries.finish_method_query)
        finish_method_clean = clean_string(finish_method_raw)
        self._finish_method = finish_method_clean

        if "decision" in finish_method_clean.lower():
            decision = finish_method_clean.split(" - ")
            self._primary_finish_method = decision[0].lower()
            self._secondary_finish_method = decision[1].lower()
        else:
            self._primary_finish_method = finish_method_clean.lower()
            secondary_finish_method_raw = self._safe_css_get(
                query=self._css_queries.secondary_finish_method_query,
                xpath=self._css_queries.secondary_finish_method_xpath,
            )
            self._secondary_finish_method = clean_string(
                secondary_finish_method_raw
            ).lower()

    def _get_finish_round(self) -> None:
        finish_round_raw = self._safe_css_get(
            query=self._css_queries.finish_round_query,
            xpath=self._css_queries.next_element_xpath,
        )
        self._finish_round = int(clean_string(finish_round_raw))

        finish_time_raw = self._safe_css_get(
            query=self._css_queries.finish_time_query,
            xpath=self._css_queries.next_element_xpath,
        )
        finish_time = clean_string(finish_time_raw).split(":")
        self._finish_time_minute = int(finish_time[0])
        self._finish_time_second = int(finish_time[1])

    def _get_referee(self) -> None:
        referee_raw = self._safe_css_get(self._css_queries.referee_query)
        self._referee = clean_string(referee_raw)

    def _get_judges(self) -> None:
        judge_and_referee_list = self._safe_css_get_all(
            query=self._css_queries.judges_query,
            xpath=self._css_queries.span_text_xpath,
        )
        self._judge_1 = ""
        self._judge_2 = ""
        self._judge_3 = ""

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
        self._get_event_id()
        self._get_fighter_ids()
        self._get_weight_class()
        self._get_num_rounds()
        self._get_finish_method()
        self._get_finish_round()
        self._get_referee()
        self._get_judges()

        return Fight(
            scraped_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            fight_id=self._id,
            event_id=self._event_id,
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
