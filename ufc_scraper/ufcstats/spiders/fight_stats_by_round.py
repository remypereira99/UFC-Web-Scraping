"""Spider to crawl all fight URLs on ufcstats.com and parse fight statistics per round per fighter."""

from typing import Any

import scrapy
from scrapy.http import Response

from ufc_scraper.parsers.fight_stat_parser import FightStatByRoundParser


class CrawlFightStatsByRound(scrapy.Spider):
    """Crawl all fight URLs from ufcstats.com and yield fight statistics per round per fighter."""

    name = "crawl_fight_stats_by_round"

    custom_settings = {
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_MAX_DELAY": 10,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    start_urls = ["http://www.ufcstats.com/statistics/events/completed?page=all"]

    def parse(self, response: Response) -> Any:
        """Parse the events listing page and schedule requests to event pages."""
        yield from self._get_event_urls(response)

    def _get_event_urls(self, response: Response) -> Any:
        """Get all event urls from main event page."""
        yield from response.follow_all(
            response.css("a[href*='event-details']::attr(href)").getall(),
            callback=self._get_fight_urls,
        )

    def _get_fight_urls(self, response: Response) -> Any:
        """Get all fight urls from each event page."""
        yield from response.follow_all(
            response.css("a[href*='fight-details']::attr(href)").getall(),
            callback=self._get_fight_stats_by_round,
        )

    def _get_fight_stats_by_round(self, response: Response) -> Any:
        fight_stat_by_round_parser = FightStatByRoundParser(response)
        fight_stats_by_round = fight_stat_by_round_parser.parse_response()

        for fight_stats in fight_stats_by_round:
            yield fight_stats
