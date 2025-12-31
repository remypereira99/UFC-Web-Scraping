# UFC Web Scraping

A Scrapy-based web scraping app for extracting UFC fight data from [ufcstats.com](http://ufcstats.com). This project collects detailed information about events, fights, fighters, and fight statistics with support for both aggregate and round-by-round data.

## Features

- **Event Data**: Scrape UFC event details including name, date, location, and fight listings
- **Fight Information**: Extract fight metadata such as weight class, rounds, finish methods, and officials
- **Fighter Profiles**: Collect fighter biographies including physical stats, records, and career opponents
- **Fight Statistics**: Fight metrics including round-by-round metrics (strikes, takedowns, control time, etc.)

All spiders are configured with respectful rate limiting:
- 1 second download delay
- Randomized delay to appear more natural
- Adjust in spider `custom_settings` if needed

## Getting Started

You can crawl everything with `make crawl_all`. You can also run specific spiders with `make crawl_%` - for example, if you just want to crawl fighter metrics, run `make crawl_fighters`.

## Development

### Adding a New Data Field

1. Update the relevant dataclass in `entities.py`
2. Add extraction logic to the corresponding parser in `parsers.py`
3. Update constants in `constants.py` if needed
4. Add test coverage in `tests/parser_tests/`

## License

This project is open source. Please respect ufcstats.com's terms of service and use rate limiting when scraping.

## Acknowledgments

Data source: [UFCStats.com](http://ufcstats.com)

## Contact

For questions or feedback, please feel free to open an issue on GitHub or email me on remy.pereira@hotmail.co.uk
