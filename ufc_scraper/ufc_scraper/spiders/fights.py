from collections import defaultdict
from typing import Dict, List, Optional, Any

import scrapy

from ufc_scraper.utils import (
    get_uuid_string,
    get_fighters
)

class GetFights(scrapy.Spider):
    name: str = "get_fights"

    custom_settings: Dict[str, Any] = {
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
    }

    async def start(self):
        urls: List[str] = ["http://www.ufcstats.com/statistics/events/completed?page=all"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def get_event_urls(self, response):
        event_links: List[str] = response.css('a.b-link::attr(href)').getall()
        for link in event_links:
            yield scrapy.Request(link, callback=self.get_fight_urls)

    def get_fight_urls(self, response):
        fight_links: List[str] = response.css('a.b-flag::attr(href)').getall()
        for link in fight_links:
            yield scrapy.Request(link, callback=self.get_fights)

    def get_fights(self, response):
        fight_dict: defaultdict = defaultdict()

        fight_url: str = response.url
        fight_dict["fight_id"] = get_uuid_string(fight_url)
        fight_dict["url"] = fight_url

        event_url: str = response.css('a.b-link::attr(href)').get()
        event_id: str = get_uuid_string(event_url)
        fight_dict["event_id"] = event_id

        fighters = get_fighters(response)

        yield(fight_dict)
