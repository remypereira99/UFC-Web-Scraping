"""Spider to crawl all event URLs ufcstats.com and parse event overview metrics."""

from typing import Any

import scrapy
from scrapy.http import Response

from ufcstats.parsers.event_info_parser import EventInfoParser


class CrawlEvents(scrapy.Spider):
    """Crawl all event URLs from ufcstats.com and yield event overview metrics."""

    name = "crawl_events"

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
        yield from response.follow_all(
            response.css("a[href*='event-details']::attr(href)").getall(),
            callback=self._get_events,
        )

    def _get_events(self, response: Response) -> Any:
        event_info_parser = EventInfoParser(response)
        event = event_info_parser.parse_response()

        yield (event)
