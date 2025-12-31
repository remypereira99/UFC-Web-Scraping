.ONESHELL:
PROJECT_DIR := ufc_scraper
CRAWL := uv run scrapy scrawl

crawl_%:
	cd $(PROJECT_DIR)
	$(CRAWL) crawl_$* $(ARGS)

csv_crawl_%:
	cd $(PROJECT_DIR)
	$(CRAWL) crawl_$* -O data/$*.csv $(ARGS)

json_crawl_%:
	cd $(PROJECT_DIR)
	$(CRAWL) crawl_$* -O data/$*.json $(ARGS)
