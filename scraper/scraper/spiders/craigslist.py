# coding:utf8

import json
import random
import time

import scrapy
from scrapy.conf import settings
from six.moves.urllib.parse import urlparse, parse_qs
from utils import REGIONS_LIST


class CraigslistSpider(scrapy.Spider):
    name = "craigslist_spider"
    headers = {
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Referer': 'https://www.google.com/',
    }
    cookies = {
        'cl_b': 'ePCrP-iM6RGhrVMCTQ5NLQfiT7s',
        'cl_tocmode': 'sss%3Agrid',
    }

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 5,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 5,
    }

    def start_requests(self):
        yield scrapy.Request(settings['SPIDER_CONFIG_URL'], callback=self.start_requests2, dont_filter=True)

    def start_requests2(self, response):
        data = json.loads(response.body)
        data_dict = dict()
        for each in data:
            data_dict[each['source']] = {'url': each['url'], 'id': each['id']}

        start_url = data_dict['craigslist']['url']
        self.setting_id = data_dict['craigslist']['id']
        # start_url_func = settings['START_URL']
        # start_url = start_url_func('craigslist')
        if start_url:
            keyword = parse_qs(urlparse(start_url).query)['query'][0].split('-')[0].strip()

            for region in REGIONS_LIST["craigslist"]:
                url = start_url.format(region=region)
                yield scrapy.Request(url, headers=self.get_random_user_agent(), callback=self.parse,
                                     cookies=self.cookies, dont_filter=True,
                                     meta={'keyword': keyword.upper(), 'region': region}, priority=1)

            yield scrapy.FormRequest(settings['SPIDER_STATUS_URL'], callback=self.status_post_page,
                                     formdata={'id': str(self.setting_id), 'status': "Scanning Craigslist"}, priority=2)

    def status_post_page(self, response):
        self.logger.info(response.body)

    def parse(self, response):
        for each in response.css('.result-row'):
            item = dict()
            item['outid'] = str(each.css('::attr(data-pid)').extract_first())
            item['url'] = each.css('.result-image::attr(href)').extract_first()
            item['title'] = each.css('.result-title::text').extract_first()
            item['location'] = each.css('.result-hood::text').extract_first() or response.meta['region']
            item['keyword'] = response.meta['keyword']
            item['created'] = str(int(time.time()))
            item['source'] = "craigslist"
            data_ids = each.css('.result-image::attr(data-ids)').extract_first()
            if data_ids:
                thumbnail = ["https://images.craigslist.org/{}_300x300.jpg".format(id.split(':')[-1]) for id in
                             data_ids.split(',')][0]
            else:
                thumbnail = ""
            item['thumbnail'] = thumbnail

            post_data = item
            post_url = settings['POST_URL']
            yield scrapy.FormRequest(post_url, callback=self.post_page, formdata=post_data, dont_filter=True,
                                     meta={'post_data': post_data})

        next_page = response.css('a[title="next page"]::attr(href)').extract_first()
        if next_page:
            next_url = response.urljoin(next_page)

            yield scrapy.Request(next_url, dont_filter=True, callback=self.parse, headers=self.get_random_user_agent(),
                                 cookies=self.cookies, meta=response.meta)

    def post_page(self, response):
        self.logger.info(response.body)
        pass

    def get_random_user_agent(self):
        user_agent_list = settings["MY_USER_AGENT"]
        user_agent = user_agent_list[random.randint(0, len(user_agent_list) - 1)]
        headers = self.headers
        headers['User-Agent'] = user_agent
        return headers
