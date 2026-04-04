"""Parser for fightodds.io GraphQL JSON event responses."""

from datetime import datetime, timezone
from typing import Any, Dict, Iterator

from fightodds.fightodds.entities.event import Event
from utils import clean_string, get_uuid_string


class EventParser:
    """Parses GraphQL JSON responses from fightodds.io event pages.

    Parses key attributes of a UFC event and yields an Event dataclass.

    Args:
        event_meta: Dict containing pk, id, slug, name, date, city, state,
            and country for the event, passed from the spider via cb_kwargs.
        response: The Scrapy HTTP response containing a JSON body.

    Attributes:
        _event_meta (dict): Event metadata from the events list query.
        _fight_offer_table (dict): The eventOfferTable node from the GQL response.

    """

    def __init__(self, event_meta: Dict[str, str], response: Any) -> None:
        self._event_meta = event_meta
        self._fight_offer_table = response.json()["data"]["eventOfferTable"]

    def _get_event_location(self) -> None:
        self._city = None
        self._state = None
        self._country = None
        location_raw = self._event_meta.get("city")
        if not location_raw:
            return
        parts = clean_string(location_raw).split(", ")
        if len(parts) == 3:
            self._city, self._state, self._country = parts
        elif len(parts) == 2:
            self._city, self._country = parts
        elif len(parts) == 1:
            self._city = parts[0]

    def _get_fight_slugs(self) -> None:
        edges = self._fight_offer_table["fightOffers"]["edges"]
        slugs = [
            edge["node"]["slug"] for edge in edges if not edge["node"]["isCancelled"]
        ]
        self._fight_slugs = ", ".join(slugs)
        self._fight_ids = ", ".join(
            get_uuid_string(slug, should_format_href=False) for slug in slugs
        )

    def parse_response(self) -> Iterator[Event]:
        """Parse the JSON response to get event overview attributes.

        Returns:
            Iterator[Event]: Yields one Event dataclass.

        """
        self._get_event_location()
        self._get_fight_slugs()

        yield Event(
            scraped_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            event_pk=self._event_meta["pk"],
            event_id=self._event_meta.get("id"),
            event_slug=self._event_meta["slug"],
            event_name=clean_string(self._event_meta["name"]),
            event_date=self._event_meta["date"],
            event_city=self._city,
            event_state=self._state,
            event_country=self._country,
            fight_slugs=self._fight_slugs,
            fight_ids=self._fight_ids,
        )
