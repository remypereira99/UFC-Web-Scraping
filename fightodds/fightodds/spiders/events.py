"""Defines the spider to crawl all UFC events from fightodds.io and parse event overview metrics."""

from datetime import datetime
import json
from typing import Any, Dict

import scrapy
from glom import glom  # type: ignore[import-untyped]

from fightodds.parsers.event_parser import EventParser
from .constants import (
    FIGHTODDS_API_URL as URL,
    FIGHTODDS_API_HEADERS as HEADERS,
    FIGHTODDS_API_GQL_EVENTS_LIST_QUERY as GQL_EVENTS_LIST_QUERY,
    FIGHTODDS_API_GQL_EVENT_FIGHTERS_QUERY as GQL_EVENT_FIGHTERS_QUERY,
)


class CrawlEvents(scrapy.Spider):
    """Crawl all UFC events from fightodds.io and yield event overview metrics."""

    name = "crawl_events"

    custom_settings = {
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_MAX_DELAY": 10,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    def __init__(
        self,
        start_date: str | None = None,
        end_date: str | None = datetime.now().strftime("%Y-%m-%d"),
        num_requests: int | None = None,
        **kwargs: Any,
    ):
        """Initialise spider with optional date range filters.

        Args:
            start_date: Include events on or after this date (YYYY-MM-DD).
            end_date: Include events before this date (YYYY-MM-DD).
            num_requests: Maximum number of events to fetch.
            **kwargs: Passed through to the scrapy.Spider base class.

        """
        super().__init__(**kwargs)
        self._start_date = start_date
        self._end_date = end_date
        self._num_requests = num_requests

    def start_requests(self, after: str = "") -> Any:
        """Issue the initial events list request, with optional pagination cursor."""
        payload = {
            "operationName": "EventsListQuery",
            "variables": {
                "promotionSlug": "ufc",
                "after": after,
                "first": self._num_requests,
                "orderBy": "-date",
                "dateGte": self._start_date,
                "dateLt": self._end_date,
            },
            "query": GQL_EVENTS_LIST_QUERY,
        }
        yield scrapy.Request(
            url=URL,
            method="POST",
            headers=HEADERS,
            body=json.dumps(payload),
            callback=self._get_event_slugs,
        )

    def _get_event_slugs(self, response: Any) -> Any:
        """Extract event metadata from the events list response and paginate if needed."""
        json_response = response.json()
        events_data = glom(json_response, "data.promotion.events")
        event_edges = events_data["edges"]

        for edge in event_edges:
            node = edge["node"]
            event_meta = {
                "pk": node["pk"],
                "id": node.get("id"),
                "slug": node["slug"],
                "name": node["name"],
                "date": node["date"],
                "city": node.get("city"),
                "state": node.get("state"),
                "country": node.get("country"),
            }
            payload = {
                "operationName": "EventFightersQuery",
                "variables": {"eventPk": node["pk"]},
                "query": GQL_EVENT_FIGHTERS_QUERY,
            }
            yield scrapy.Request(
                url=URL,
                method="POST",
                headers=HEADERS,
                body=json.dumps(payload),
                callback=self._get_event_fighters,
                cb_kwargs={"event_meta": event_meta},
            )

        page_info = events_data["pageInfo"]
        if page_info["hasNextPage"]:
            yield from self.start_requests(after=page_info["endCursor"])

    def _get_event_fighters(self, response: Any, event_meta: Dict[str, str]) -> Any:
        """Parse per-event fight slugs and yield an Event item."""
        event_parser = EventParser(event_meta, response)
        yield from event_parser.parse_response()
