.ONESHELL:
PROJECT_DIR := ufc_scraper

crawl_%:
	cd $(PROJECT_DIR)
	uv run scrapy crawl crawl_$* $(ARGS)

csv_crawl_%:
	cd $(PROJECT_DIR)
	uv run scrapy crawl crawl_$* -O data/$*.csv $(ARGS)

json_crawl_%:
	cd $(PROJECT_DIR)
	uv run scrapy crawl crawl_$* -O data/$*.json $(ARGS)
