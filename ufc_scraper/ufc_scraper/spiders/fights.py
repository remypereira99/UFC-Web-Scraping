from collections import defaultdict
from typing import Any, AsyncGenerator, Dict, List, Union

import scrapy
from scrapy.http import Response

from utils import (
    get_uuid_string,
    get_fighters,
    get_fight_info,
    get_fight_stats,
)


class CrawlFights(scrapy.Spider):
    name: str = "crawl_fights"

    custom_settings: Dict[Any, Any] = {
        "DOWNLOAD_DELAY": 1,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    async def start(self) -> AsyncGenerator[Any, Any]:
        urls: List[str] = ["http://www.ufcstats.com/statistics/events/completed?page=2"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.get_event_urls)

    def get_event_urls(self, response: Response) -> Any:
        event_links: List[str] = response.css("a.b-link::attr(href)").getall()
        for link in event_links:
            yield scrapy.Request(link, callback=self.get_fight_urls)

    def get_fight_urls(self, response: Response) -> Any:
        fight_links: List[str] = response.css("a.b-flag::attr(href)").getall()
        for link in fight_links:
            yield scrapy.Request(link, callback=self.get_fights)

    def get_fights(self, response: Response) -> Any:
        fight_dict: defaultdict[str, Union[str, int]] = defaultdict()

        fight_url: str = response.url
        fight_dict["fight_id"] = get_uuid_string(fight_url)
        fight_dict["url"] = fight_url

        event_url_query: str = "a.b-link::attr(href)"
        event_url: Union[str, None] = response.css(event_url_query).get()
        if not event_url:
            raise ValueError(
                f"Event url missing from {response.url} with query {event_url_query}"
            )
        event_id: str = get_uuid_string(event_url)
        fight_dict["event_id"] = event_id

        temp_fight_dicts = []
        temp_fight_dicts.append(get_fighters(response))
        temp_fight_dicts.append(get_fight_info(response))
        temp_fight_dicts.append(get_fight_stats(response))

        for temp_dict in temp_fight_dicts:
            for key in temp_dict.keys():
                fight_dict[key] = temp_dict[key]

        yield (fight_dict)
