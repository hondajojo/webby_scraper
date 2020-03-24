from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from twisted.internet.task import deferLater

from scraper.spiders.craigslist_rss import CraigslistRssSpider


# http://crawl.blog/scrapy-loop/


def sleep(self, *args, seconds):
    """Non blocking sleep callback"""
    return deferLater(reactor, seconds, lambda: None)


def main():
    process = CrawlerProcess(get_project_settings())

    def _crawl(result, spider):
        deferred = process.crawl(spider)
        deferred.addCallback(lambda results: print('waiting 60 seconds before restart...'))
        deferred.addCallback(sleep, seconds=60)
        deferred.addCallback(_crawl, spider)
        return deferred

    _crawl(None, CraigslistRssSpider)
    process.start()


if __name__ == '__main__':
    main()
