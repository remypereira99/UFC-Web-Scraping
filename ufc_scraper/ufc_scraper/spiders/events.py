from typing import List, Any

import scrapy
from scrapy.http import Response

from parsers import EventInfoParser


class CrawlEvents(scrapy.Spider):
    name = "crawl_events"

    custom_settings = {
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_MAX_DELAY": 10,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    start_urls = [
        "http://www.ufcstats.com/statistics/events/completed?page=all"
    ]

    def parse(self, response: Response) -> Any:
        yield from response.follow_all(
            css="a.b-link::attr(href)",
            callback=self._get_events,
        )

    def _get_events(self, response: Response) -> Any:
        event_info_parser = EventInfoParser(response)
        event = event_info_parser.parse_response()

        yield (event)
