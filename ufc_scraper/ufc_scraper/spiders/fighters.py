from typing import Any

import scrapy
from scrapy.http import Response

from parsers import FighterInfoParser


class CrawlFighters(scrapy.Spider):
    name = "crawl_fighters"

    custom_settings = {
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_MAX_DELAY": 10,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    start_urls = [
        f"http://ufcstats.com/statistics/fighters?char={letter}&page=all"
        for letter in "abcdefghijklmnopqrstuvwxyz"
    ]

    def parse(self, response: Response) -> Any:
        yield from response.follow_all(
            css="a.b-link::attr(href)",
            callback=self._get_fighters,
        )

    def _get_fighters(self, response: Response) -> Any:
        fighter_info_parser = FighterInfoParser(response)
        fighter = fighter_info_parser.parse_response()

        yield (fighter)
