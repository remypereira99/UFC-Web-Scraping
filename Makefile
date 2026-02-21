PROJECT_DIR := ufcstats
CRAWL := uv run scrapy crawl
CRAWL_LIST := events fighters fights fight_stats fight_stats_by_round
.PHONY: crawl_all crawl_all_output

# Crawl and output to a specific format, e.g. csv, json
crawl_with_output_%:
	cd $(PROJECT_DIR) && \
	$(CRAWL) crawl_$* $(if $(OUTPUT),-O data/$*.$(OUTPUT)) $(ARGS)


crawl_all_output:
	@for c in $(CRAWL_LIST); do \
		$(MAKE) crawl_with_output_$$c OUTPUT=$(OUTPUT) $(ARGS); \
	done


crawl_%:
	cd $(PROJECT_DIR) && \
	$(CRAWL) crawl_$* $(ARGS)


crawl_all:
	@for c in $(CRAWL_LIST); do \
		$(MAKE) crawl_$$c $(ARGS); \
	done
