from typing import Any, AsyncGenerator, Dict, List

import scrapy
from scrapy.http import Response

from utils import get_fight_info


class CrawlFights(scrapy.Spider):
    name: str = "crawl_fights"

    custom_settings: Dict[Any, Any] = {
        "DOWNLOAD_DELAY": 1,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    async def start(self) -> AsyncGenerator[Any, Any]:
        urls: List[str] = ["http://www.ufcstats.com/statistics/events/completed?page=2"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self._get_event_urls)

    def _get_event_urls(self, response: Response) -> Any:
        event_links: List[str] = response.css("a.b-link::attr(href)").getall()
        for link in event_links:
            yield scrapy.Request(link, callback=self._get_fight_urls)

    def _get_fight_urls(self, response: Response) -> Any:
        fight_links: List[str] = response.css("a.b-flag::attr(href)").getall()
        for link in fight_links:
            yield scrapy.Request(link, callback=self._get_fights)

    def _get_fights(self, response: Response) -> Any:
        fight = get_fight_info(response)

        yield fight
