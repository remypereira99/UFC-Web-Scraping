"""Constants file for parser classes."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional

from scrapy.http import Response

from utils import get_uuid_string


class _Parser(ABC):
    def __init__(self, response: Response):
        self._response = response
        self._url = self._response.url
        self._id = get_uuid_string(self._url)
        self._css_queries = CssQueries()

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


@dataclass(frozen=True)
class CssQueries:
    """Collection of CSS selectors used for scraping fight, event, and fighter data.

    Each attribute represents a CSS query string targeting a specific element
    on the page. The class is immutable and intended to be used as a constants
    container for web scraping logic.
    """

    href_query: str = "a.b-link::attr(href)"
    event_urls_query: str = "a[href*='event-details']::attr(href)"
    fight_urls_query: str = "a[href*='fight-details']::attr(href)"
    fighter_urls_query: str = "a.b-link.b-fight-details__person-link::attr(href)"
    bout_type_query: str = "i.b-fight-details__fight-title::text"
    round_text_query: str = ".b-fight-details__label:contains('Round:')"
    finish_method_query: str = ".b-fight-details__label:contains('Method:') + i::text"
    secondary_finish_method_query: str = ".b-fight-details__label:contains('Details:')"
    finish_round_query: str = ".b-fight-details__label:contains('Round:')"
    finish_time_query: str = ".b-fight-details__label:contains('Time:')"
    referee_query: str = ".b-fight-details__label:contains('Referee:') + span::text"
    judges_query: str = "i.b-fight-details__text-item"
    fighter_name_query: str = "span.b-content__title-highlight::text"
    fighter_nickname_query: str = "p.b-content__Nickname::text"
    fighter_stats_query: str = "li.b-list__box-list-item::text"
    fighter_record_query: str = "span.b-content__title-record::text"
    fighter_fights_query: str = "a[href*='fight-details']::attr(href)"
    event_name_query: str = "span.b-content__title-highlight::text"
    fight_stat_headers_query: str = (
        "thead.b-fight-details__table-head th.b-fight-details__table-col::text"
    )
    round_headers_query: str = (
        "thead.b-fight-details__table-row th.b-fight-details__table-col::text"
    )
    fight_stat_values_query: str = (
        "tbody.b-fight-details__table-body p.b-fight-details__table-text::text"
    )


WEIGHT_CLASSES_LOWER: List[str] = [
    "women's strawweight",
    "women's flyweight",
    "women's bantamweight",
    "women's featherweight",
    "flyweight",
    "bantamweight",
    "featherweight",
    "lightweight",
    "welterweight",
    "middleweight",
    "light heavyweight",
    "heavyweight",
    "catch weight",
    "open weight",
]

TOTALS_STATS_EXPECTED_HEADERS: List[str] = [
    "KD",
    "Sig. str.",
    "Sig. str. %",
    "Total str.",
    "Td",
    "Td %",
    "Sub. att",
    "Rev.",
    "Ctrl",
]
SIGNIFICANT_STRIKES_EXPECTED_HEADERS: List[str] = [
    "Sig. str",
    "Sig. str. %",
    "Head",
    "Body",
    "Leg",
    "Distance",
    "Clinch",
    "Ground",
]
