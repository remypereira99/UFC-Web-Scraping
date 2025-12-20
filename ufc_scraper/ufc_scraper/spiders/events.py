from typing import Dict, List, Any

import scrapy
from scrapy.http import Response

from parsers import EventInfoParser


class CrawlEvents(scrapy.Spider):
    name: str = "crawl_events"

    custom_settings: Dict[Any, Any] = {
        "DOWNLOAD_DELAY": 1,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    start_urls: List[str] = [
        "http://www.ufcstats.com/statistics/events/completed?page=all"
    ]

    def parse(self, response: Response) -> Any:
        event_links: List[str] = response.css("a.b-link::attr(href)").getall()
        for link in event_links:
            yield scrapy.Request(link, callback=self._get_events)

    def _get_events(self, response: Response) -> Any:
        event_info_parser = EventInfoParser(response)
        event = event_info_parser.parse_response()

        yield (event)
