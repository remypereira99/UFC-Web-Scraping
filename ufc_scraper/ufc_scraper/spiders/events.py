from collections import defaultdict
from typing import Dict, List, Any

import scrapy
from scrapy.http import Response

from utils import get_uuid_string, get_event_info, get_event_fights


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
            yield scrapy.Request(link, callback=self.get_events)

    def get_events(self, response: Response) -> Any:
        event_dict: defaultdict[str, str] = defaultdict()

        event_url: str = response.url
        event_dict["event_id"] = get_uuid_string(event_url)
        event_dict["url"] = event_url

        event_info: Dict[str, str] = get_event_info(response)

        for key in event_info.keys():
            event_dict[key] = event_info[key]

        event_fights: str = get_event_fights(response)
        event_dict["fights"] = event_fights

        yield (event_dict)
