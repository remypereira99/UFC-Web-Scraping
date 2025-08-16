from collections import defaultdict

import scrapy

from ufc_scraper.utils import (
    get_uuid_string,
    get_event_info,
    get_event_fights
)

class GetEvents(scrapy.Spider):
    name = "get_events"

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
    }

    start_urls = ["http://www.ufcstats.com/statistics/events/completed?page=all"]

    def parse(self, response):
        event_links = response.css('a.b-link::attr(href)').getall()
        scraped_links = []
        for link in event_links:
            if link not in scraped_links:
                scraped_links.append(link)
                yield scrapy.Request(link, callback=self.get_event_info)

    def get_event_info(self, response):
        event_dict = defaultdict()

        event_url = response.url
        event_dict["event_id"] = get_uuid_string(event_url)
        event_dict["url"] = event_url

        yield(event_dict)
