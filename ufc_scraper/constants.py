from dataclasses import dataclass
from typing import List

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
