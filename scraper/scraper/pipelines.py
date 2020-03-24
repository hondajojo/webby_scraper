# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


from .basedb import DB
from sqlite3 import IntegrityError


class ScraperPipeline(object):
    def __init__(self):
        self.db = DB()

    def process_item(self, item, spider):
        try:
            self.db._insert("scraper_craigslist", **item)
            self.db.commit()
        except IntegrityError:
            pass
        return item
