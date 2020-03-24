from scrapy import signals
import requests


class SpiderCtlExtension(object):
    def __init__(self, url):
        self.url = url

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls(url=crawler.settings.get('SPIDER_STATUS_URL'))
        ext.project_name = crawler.settings.get('BOT_NAME')
        # crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)

        return ext

    # def spider_opened(self, spider):
    #     pass

    def spider_closed(self, spider, reason):
        if int(spider.setting_id) > 0:
            data = {
                'id': spider.setting_id,
                'status': 'Sleeping'
            }
            print(requests.post(self.url, data).json())
