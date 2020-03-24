# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScraperItem(scrapy.Item):
    outid = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    location = scrapy.Field()
    thumbnail = scrapy.Field()
    keyword = scrapy.Field()
    created = scrapy.Field()
