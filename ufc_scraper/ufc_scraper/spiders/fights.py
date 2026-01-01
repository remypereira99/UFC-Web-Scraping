"""Defines the spider to crawl all fight URLs ufcstats.com and parse fight overview metrics."""

from typing import Any, List

import scrapy
from scrapy.http import Response

from parsers import FightInfoParser


class CrawlFights(scrapy.Spider):
    name = "crawl_fights"

    custom_settings = {
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_MAX_DELAY": 10,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    start_urls = ["http://www.ufcstats.com/statistics/events/completed?page=all"]

    def parse(self, response: Response):
        yield from self._get_event_urls(response)

    def _get_event_urls(self, response: Response) -> Any:
        yield from response.follow_all(
            css="a.b-link::attr(href)",
            callback=self._get_fight_urls,
        )

    def _get_fight_urls(self, response: Response) -> Any:
        yield from response.follow_all(
            css="a.b-link::attr(href)",
            callback=self._get_fights,
        )

    def _get_fights(self, response: Response) -> Any:
        fight_info_parser = FightInfoParser(response)
        fight = fight_info_parser.parse_response()

        yield fight
