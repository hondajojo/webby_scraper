# coding:utf8

import json
import random
import time

import scrapy
from scrapy.conf import settings
from six.moves.urllib.parse import urlparse, parse_qs


class EbaySpider(scrapy.Spider):
    name = "ebay_spider"
    headers = {
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Referer': 'https://www.google.com/',
    }

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 5,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 5,
    }

    def start_requests(self):
        yield scrapy.Request(settings['SPIDER_CONFIG_URL'], callback=self.start_requests2)

    def start_requests2(self, response):
        # start_url_func = settings['START_URL']
        # start_url = start_url_func('ebay')

        data = json.loads(response.body)
        data_dict = dict()
        for each in data:
            data_dict[each['source']] = {'url': each['url'], 'id': each['id']}

        start_url = data_dict['ebay']['url']
        self.setting_id = data_dict['ebay']['id']

        if start_url:
            keyword = parse_qs(urlparse(start_url).query)['_nkw'][0].strip()

            for region in settings["REGIONS_LIST"]["ebay"]:
                url = start_url.format(region=region)
                yield scrapy.Request(url, headers=self.get_random_user_agent(), callback=self.parse, dont_filter=True,
                                     meta={'keyword': keyword.upper()}, priority=1)

            yield scrapy.FormRequest(settings['SPIDER_STATUS_URL'], callback=self.status_post_page,
                                     formdata={'id': str(self.setting_id), 'status': "Scanning Ebay"}, priority=2)

    def status_post_page(self, response):
        self.logger.info(response.body)

    def parse(self, response):
        for each in response.css('.srp-river-results .s-item'):
            item = dict()
            item['title'] = each.css('.s-item__title::text').extract_first()
            item['url'] = each.css('.s-item__link::attr(href)').extract_first()
            item['outid'] = urlparse(item['url']).path.split('/')[-1]
            thumbnail = each.css('.s-item__image-img::attr(data-src)').extract_first()
            if not thumbnail:
                thumbnail = each.css('.s-item__image-img::attr(src)').extract_first() or ""

            item['location'] = each.css('.s-item__itemLocation::text').extract_first()
            item['keyword'] = response.meta['keyword']
            item['thumbnail'] = thumbnail
            item['created'] = str(int(time.time()))
            item['source'] = "ebay"

            post_data = item
            post_url = settings['POST_URL']
            yield scrapy.FormRequest(post_url, callback=self.post_page, formdata=post_data, dont_filter=True,
                                     meta={'post_data': post_data})

        current_page = response.css('.x-pagination__li--selected a::text').extract_first()
        next_url = response.css('a[rel="next"]::attr(href)').extract_first()
        next_page = parse_qs(urlparse(next_url).query)['_pgn'][0]
        if int(next_page) > int(current_page):
            yield scrapy.Request(next_url, dont_filter=True, callback=self.parse, headers=self.get_random_user_agent(),
                                 meta=response.meta)

    def post_page(self, response):
        self.logger.info(response.body)
        pass

    def get_random_user_agent(self):
        user_agent_list = settings["MY_USER_AGENT"]
        user_agent = user_agent_list[random.randint(0, len(user_agent_list) - 1)]
        headers = self.headers
        headers['User-Agent'] = user_agent
        return headers
