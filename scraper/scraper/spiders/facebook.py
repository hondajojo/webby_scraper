# coding:utf8

import random
import time

import scrapy
from scrapy.conf import settings
from six.moves.urllib.parse import urlparse, parse_qs


class FacebookSpider(scrapy.Spider):
    name = "facebook_spider"
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
        start_url = settings['START_URL']
        keyword = settings['KEYWORD']

        # for each_url in start_url:
        #     for region in settings["REGIONS_LIST"]['ebay']:
        #         url = each_url.format(region=region)
        #         yield scrapy.Request(url, headers=self.get_random_user_agent(), callback=self.parse, dont_filter=True,
        #                              meta={'keyword': keyword.upper()})

        # yield scrapy.Request(
        #     "https://www.ebay.com/sch/Motorcycles/6024/i.html?_from=R40&_nkw=triumph&UF_single_selection=Make%3ATriumph&UF_context=finderType%3AVEHICLE_FINDER&_sacat=6024&_stpos=54911&_fspt=1&_sadis=1000&_pgn=1",
        #     headers=self.get_random_user_agent(), callback=self.parse, dont_filter=True,
        #     meta={'keyword': "123"})

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

            print(item)

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
