"""Defines the spider to crawl all fighter slugs from fightodds.io and parse fighter stats."""

import json
from typing import Any

import scrapy

from fightodds.parsers.fighter_parser import FighterParser
from .constants import (
    FIGHTODDS_API_URL as URL,
    FIGHTODDS_API_HEADERS as HEADERS,
    FIGHTODDS_API_GQL_FIGHTERS_LIST_QUERY as GQL_FIGHTERS_LIST_QUERY,
    FIGHTODDS_API_GQL_FIGHTER_STATS_QUERY as GQL_FIGHTER_STATS_QUERY,
)


class CrawlFighters(scrapy.Spider):
    """Crawl all fighter slugs from fightodds.io and yield fighter stats."""

    name = "crawl_fighters"

    custom_settings = {
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_MAX_DELAY": 10,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    def __init__(
        self,
        num_requests: int | None = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self._num_requests = num_requests

    def start_requests(self, after: str | None = None) -> Any:
        """Issue the initial fighters list request, with optional pagination cursor."""
        payload = {
            "operationName": "FightersListQuery",
            "variables": {
                "after": after,
                "first": self._num_requests,
            },
            "query": GQL_FIGHTERS_LIST_QUERY,
        }
        yield scrapy.Request(
            url=URL,
            method="POST",
            headers=HEADERS,
            body=json.dumps(payload),
            callback=self._get_fighter_slugs,
        )

    def _get_fighter_slugs(self, response: Any) -> Any:
        """Extract fighter slugs from the fighters list response and paginate if needed."""
        json_response = response.json()
        fighters_data = json_response["data"]["allFighters"]

        for edge in fighters_data["edges"]:
            fighter_slug: str = edge["node"]["slug"]
            payload = {
                "operationName": "FighterStatsQuery",
                "variables": {"fighterSlug": fighter_slug},
                "query": GQL_FIGHTER_STATS_QUERY,
            }
            yield scrapy.Request(
                url=URL,
                method="POST",
                headers=HEADERS,
                body=json.dumps(payload),
                callback=self._get_fighter,
            )

        page_info = fighters_data["pageInfo"]
        if page_info["hasNextPage"] and page_info["endCursor"]:
            yield from self.start_requests(after=page_info["endCursor"])

    def _get_fighter(self, response: Any) -> Any:
        """Parse per-fighter stats and yield a Fighter item."""
        fighter_parser = FighterParser(response)
        yield from fighter_parser.parse_response()
