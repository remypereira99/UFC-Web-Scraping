from abc import ABC, abstractmethod
from typing import Any

from scrapy.http import Response

from constants import WEIGHT_CLASSES_LOWER
from entities import Fight
from utils import clean_string, get_uuid_string, safe_css_get


class Parser(ABC):
    def __init__(self, response: Response):
        self._response = response
        self._url: str = self._response.url
        self._id: str = get_uuid_string(self._url)

    @abstractmethod
    def parse_response(self) -> Any:
        pass


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
        bout_type_raw = safe_css_get(self._response, self._bout_type_query)
        bout_type_clean = clean_string(bout_type_raw)
        self._weight_class = (
            bout_type_clean if bout_type_clean.lower() in WEIGHT_CLASSES_LOWER else ""
        )

    def _get_num_rounds(self) -> None:
        num_rounds_raw = safe_css_get(
            self._response, self._round_text_query, xpath=self._next_element_xpath
        )
        self._num_rounds = int(clean_string(num_rounds_raw))

    def _get_finish_method(self) -> None:
        finish_method_raw = safe_css_get(self._response, self._finish_method_query)
        finish_method_clean = clean_string(finish_method_raw)

        if "decision" in finish_method_clean.lower():
            decision = finish_method_clean.split(" - ")
            self._finish_method = decision[0]
            self._finish_submethod = decision[1]
        else:
            self._finish_method = finish_method_clean
            finish_submethod_raw = safe_css_get(
                self._response,
                self._finish_submethod_query,
                xpath=self._finish_submethod_xpath,
            )
            self._finish_submethod = clean_string(finish_submethod_raw)

    def _get_finish_round(self) -> None:
        finish_round_raw = safe_css_get(
            self._response, self._finish_round_query, xpath=self._next_element_xpath
        )
        self._finish_round = int(clean_string(finish_round_raw))

        finish_time_raw = safe_css_get(
            self._response, self._finish_time_query, xpath=self._next_element_xpath
        )
        finish_time = clean_string(finish_time_raw).split(":")
        self._finish_time_minute = int(finish_time[0])
        self._finish_time_second = int(finish_time[1])

    def _get_referee(self) -> None:
        referee_raw = safe_css_get(
            self._response, self._finish_round_query, xpath=self._next_element_xpath
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
