from typing import Any

import scrapy
from scrapy.http import Response

from utils import get_fighter_info


class ScrapeFighters(scrapy.Spider):
    name = "scrape_fighters"

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    start_urls = [
        f"http://ufcstats.com/statistics/fighters?char={letter}&page=all"
        for letter in "abcdefghijklmnopqrstuvwxyz"
    ]

    def parse(self, response: Response) -> Any:
        fighter_links = response.css("a.b-link::attr(href)").getall()
        scraped_links = []
        for link in fighter_links:
            if link not in scraped_links:
                scraped_links.append(link)
                yield scrapy.Request(link, callback=self.get_fighters)

    def get_fighters(self, response: Response) -> Any:
        fighter = get_fighter_info(response)

        yield (fighter)
