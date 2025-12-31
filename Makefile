PROJECT_DIR := ufc_scraper

crawl_%:
	cd $(PROJECT_DIR) && \
	uv run scrapy crawl crawl_$* $(ARGS)
