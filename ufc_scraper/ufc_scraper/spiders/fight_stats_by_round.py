"""Defines the spider to crawl all fight URLs on ufcstats.com and parse fight statistics per round per fighter."""

from typing import Any, AsyncGenerator, Dict, List

import scrapy
from scrapy.http import Response

from parsers import FightStatByRoundParser


class CrawlFightStatsByRound(scrapy.Spider):
    name = "crawl_fight_stats_by_round"

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    start_urls = ["http://www.ufcstats.com/statistics/events/completed?page=all"]

    def parse(self, response: Response):
        yield from self._get_event_urls(response)

    def _get_event_urls(self, response: Response) -> Any:
        event_links: List[str] = response.css("a.b-link::attr(href)").getall()
        for link in event_links:
            yield scrapy.Request(link, callback=self._get_fight_urls)

    def _get_fight_urls(self, response: Response) -> Any:
        fight_links: List[str] = response.css("a.b-flag::attr(href)").getall()
        for link in fight_links:
            yield scrapy.Request(link, callback=self._get_fight_stats_by_round)

    def _get_fight_stats_by_round(self, response: Response) -> Any:
        fight_stat_by_round_parser = FightStatByRoundParser(response)
        fight_stats_by_round = fight_stat_by_round_parser.parse_response()

        for fight_stats in fight_stats_by_round:
            yield fight_stats
