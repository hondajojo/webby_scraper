#!/bin/sh
export PATH=$PATH:/usr/local/bin
cd /home/ubuntu/webby_scraper/scraper
nohup /home/ubuntu/.local/bin/scrapy crawl craigslist_rss_spider >>craigslist_rss_spider.log 2>&1