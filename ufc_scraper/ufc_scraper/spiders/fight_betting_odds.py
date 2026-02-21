"""Defines the spider to crawl all fight URLs from fightodds.io and parse fight betting odds."""

import json
from typing import Any

import scrapy
from glom import glom  # type: ignore[import-untyped]

from ufc_scraper.parsers.fight_odds_parser import FightOddsParser
from .constants import (
    FIGHTODDS_API_URL as URL,
    FIGHTODDS_API_HEADERS as HEADERS,
    FIGHTODDS_API_GQL_EVENT_ODDS_QUERY as GQL_EVENT_ODDS_QUERY,
    FIGHTODDS_API_GQL_EVENTS_QUERY as GQL_EVENTS_QUERY,
    FIGHTODDS_API_GQL_FIGHT_ODDS_QUERY as GQL_FIGHT_ODDS_QUERY,
)


class CrawlFightBettingOdds(scrapy.Spider):
    """Crawl all fight URLs from fightodds.io and yield betting odds per sportsbook."""

    name = "crawl_fight_betting_odds"

    custom_settings = {
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_MAX_DELAY": 10,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    def __init__(
        self, start_date: str | None = None, end_date: str | None = None, **kwargs: Any
    ):
        """Initialise spider with optional date range filters.

        Args:
            start_date: Include events on or after this date (YYYY-MM-DD).
            end_date: Include events before this date (YYYY-MM-DD).
            **kwargs: Passed through to the scrapy.Spider base class.

        """
        super().__init__(**kwargs)
        self._start_date = start_date
        self._end_date = end_date
        self._num_requests = 10

    def start_requests(self, after: str = "") -> Any:
        """Issue the initial events list request, with optional pagination cursor."""
        payload = {
            "operationName": "EventsPromotionRecentQuery",
            "variables": {
                "promotionSlug": "ufc",
                "after": after,
                "first": self._num_requests,
                "orderBy": "-date",
                "dateGte": self._start_date,
                "dateLt": self._end_date,
            },
            "query": GQL_EVENTS_QUERY,
        }
        yield scrapy.Request(
            url=URL,
            method="POST",
            headers=HEADERS,
            body=json.dumps(payload),
            callback=self._get_event_pks,
        )

    def _get_event_pks(self, response: Any) -> Any:
        """Extract event PKs from the events list response and paginate if needed."""
        json_response = response.json()
        events_data = glom(json_response, "data.promotion.events")
        event_edges = events_data["edges"]

        for edge in event_edges:
            event_pk: int = glom(edge, "node.pk")
            payload = {
                "operationName": "EventOddsQuery",
                "variables": {"eventPk": event_pk},
                "query": GQL_EVENT_ODDS_QUERY,
            }
            yield scrapy.Request(
                url=URL,
                method="POST",
                headers=HEADERS,
                body=json.dumps(payload),
                callback=self._get_fight_slugs,
            )

        page_info = events_data["pageInfo"]
        if page_info["hasNextPage"]:
            yield from self.start_requests(after=page_info["endCursor"])

    def _get_fight_slugs(self, response: Any) -> Any:
        """Extract fight slugs from an event's fight offers and request per-fight odds."""
        json_response = response.json()
        fight_edges = glom(json_response, "data.eventOfferTable.fightOffers.edges")

        for edge in fight_edges:
            if glom(edge, "node.isCancelled"):
                continue
            fight_slug: str = glom(edge, "node.slug")
            payload = {
                "operationName": "FightOddsQuery",
                "variables": {"fightSlug": fight_slug},
                "query": GQL_FIGHT_ODDS_QUERY,
            }
            yield scrapy.Request(
                url=URL,
                method="POST",
                headers=HEADERS,
                body=json.dumps(payload),
                callback=self._get_fight_odds,
            )

    def _get_fight_odds(self, response: Any) -> Any:
        """Parse per-fight odds and yield one FightOdds item per sportsbook."""
        fight_odds_parser = FightOddsParser(response)
        yield from fight_odds_parser.parse_response()
