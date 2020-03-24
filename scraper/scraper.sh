#!/bin/sh
export PATH=$PATH:/usr/local/bin
cd /usr/local/src/webby_scraper/scraper
nohup scrapy crawl craigslist_spider >>craigslist_spider.log 2>&1