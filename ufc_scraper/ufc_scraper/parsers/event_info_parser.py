"""HTML parsers for UFCStats pages.

This module contains Scrapy-based parsers for UFC events, fights,
fighters, and fight statistics (total and by-round).
"""

from datetime import datetime, timezone

from scrapy.http import Response

from ufc_scraper.parsers.base_parser import Parser
from entities import Event
from utils import clean_string, get_uuid_string


class EventInfoParser(Parser):
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
        self._event_date_location = self._safe_css_get_all(
            "li.b-list__box-list-item::text"
        )

    def _get_event_name(self) -> None:
        event_name_raw = self._safe_css_get(self._css_queries.event_name_query)
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
        fight_urls = self._safe_css_get_all(self._css_queries.fight_urls_query)
        fight_ids = [get_uuid_string(fight_url) for fight_url in fight_urls]
        self._fights = ", ".join(fight_ids)

    def parse_response(self) -> Event:
        """Parse the HTML response to get key event attributes.

        Args:
            response (Response): The response object to query.

        Returns:
            Event: Dataclass containing all key event attributes.

        """
        self._get_event_name()
        self._get_event_date()
        self._get_event_location()
        self._get_fights()

        return Event(
            scraped_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
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
