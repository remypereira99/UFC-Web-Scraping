from collections import defaultdict
import re

import scrapy

from ufc_scraper.utils import (
    get_fighter_names,
    get_fighter_personal_stats,
    get_fighter_record,
    get_fighter_opponents
)

class GetFighterLinks(scrapy.Spider):
    name = "get_fighter_links"

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
    }

    start_urls = [
        f'http://ufcstats.com/statistics/fighters?char={letter}&page=all' for letter in 'abcdefghijklmnopqrstuvwxyz'
    ]

    def parse(self, response):
        fighter_link = response.css('a.b-link::attr(href)').get()
        yield scrapy.Request(fighter_link, callback=self.get_fighter_info)

    def parse(self, response):
        fighter_links = response.css('a.b-link::attr(href)').getall()
        scraped_links = []
        for link in fighter_links:
            if link not in scraped_links:
                scraped_links.append(link)
                yield scrapy.Request(link, callback=self.get_fighter_info)

    def get_fighter_info(self, response):
        fighter_dict = defaultdict()
        
        temp_fighter_dicts = []

        temp_fighter_dicts.append(get_fighter_names(response))
        temp_fighter_dicts.append(get_fighter_personal_stats(response))
        temp_fighter_dicts.append(get_fighter_record(response))


        fighter_dict["fighter_url"] = response.url

        for temp_dict in temp_fighter_dicts:
            for key in temp_dict.keys():
                fighter_dict[key] = temp_dict[key]

        fighter_dict["opponents"] = get_fighter_opponents(response)
        

        yield(fighter_dict)
