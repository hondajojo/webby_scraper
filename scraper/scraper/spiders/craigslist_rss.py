# coding:utf8

import html
import json
import random
import time

import feedparser
import scrapy
from scrapy.conf import settings
from six.moves.urllib.parse import urlparse, parse_qs


class CraigslistRssSpider(scrapy.Spider):
    name = "craigslist_rss_spider"
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
        yield scrapy.Request(settings['SPIDER_CONFIG_URL'], callback=self.start_requests2)

    def start_requests2(self, response):
        # start_url = settings['START_URL']
        # keyword = settings['KEYWORD']
        # for each_url in start_url:
        #     for region in settings["REGIONS_LIST"]['craigslist']:
        #         url = each_url.format(region=region)
        #         url = "{}&format=rss".format(url)
        #         yield scrapy.Request(url, headers=self.get_random_user_agent(), callback=self.parse,
        #                              cookies=self.cookies,
        #                              dont_filter=True,
        #                              meta={'keyword': keyword.upper(), 'region': region})

        # start_url_func = settings['START_URL']
        # start_url = start_url_func('craigslist')

        data = json.loads(response.body)
        data_dict = dict()
        for each in data:
            data_dict[each['source']] = {'url': each['url'], 'id': each['id']}

        start_url = data_dict['craigslist']['url']
        self.setting_id = data_dict['craigslist']['id']

        if start_url:
            start_url = "{}&format=rss".format(start_url)
            keyword = parse_qs(urlparse(start_url).query)['query'][0].split('-')[0].strip()

            for region in settings["REGIONS_LIST"]["craigslist"]:
                url = start_url.format(region=region)
                yield scrapy.Request(url, headers=self.get_random_user_agent(), callback=self.parse,
                                     cookies=self.cookies, dont_filter=True,
                                     meta={'keyword': keyword.upper()}, priority=1)

            yield scrapy.FormRequest(settings['SPIDER_STATUS_URL'], callback=self.status_post_page,
                                     formdata={'id': str(self.setting_id), 'status': "Scanning Craigslist"}, priority=2)

    def status_post_page(self, response):
        self.logger.info(response.body)

    def parse(self, response):
        d = feedparser.parse(response.body)
        for each in d['entries']:
            raw_title = each['title']
            title = html.unescape(raw_title)
            raw_location = raw_title.split('&#')[0].strip()
            if raw_location.endswith(')'):
                location = raw_location.split('(')[-1].rstrip(')')
            else:
                location = ""
            item = dict()
            item['outid'] = urlparse(each['id']).path.split('/')[-1].replace('.html', '')
            item['url'] = each['id']
            item['title'] = title
            item['location'] = location
            item['keyword'] = response.meta['keyword']
            item['created'] = str(int(time.time()))
            item['source'] = "craigslist"
            if each.get('enc_enclosure'):
                thumbnail = each['enc_enclosure']['resource']
            else:
                thumbnail = ""
            item['thumbnail'] = thumbnail

            post_data = item
            post_url = settings['POST_URL']
            yield scrapy.FormRequest(post_url, callback=self.post_page, formdata=post_data, dont_filter=True)

        if len(d['entries']) == 25:
            page = response.meta.get('page', 0)
            url = "https://{}.craigslist.org/search/sss?query={}&excats=7-13-22-2-24-24-1-1-1-1-1-1-3-6-10-1-1-1-4-8-1-1-1-1-1-4-1-7-1-1-1-1-8-1-2-1-1-1-1-1-1-1-1-1-1-1-1-1-1-2-1-1-1-1-1-1-1-1-1-1-3-1-3-1-1-1-1-1-3-1-2-1&sort=date&postedToday=1&search_distance=200&postal=54911&format=rss&s={}".format(
                response.meta['region'], response.meta['keyword'], page + 25)
            response.meta.update({'page': page + 25})
            yield scrapy.Request(url, headers=self.get_random_user_agent(), callback=self.parse, cookies=self.cookies,
                                 dont_filter=True, meta=response.meta)

    def get_random_user_agent(self):
        user_agent_list = settings["MY_USER_AGENT"]
        user_agent = user_agent_list[random.randint(0, len(user_agent_list) - 1)]
        headers = self.headers
        headers['User-Agent'] = user_agent
        return headers

    def post_page(self, response):
        self.logger.info(response.body)
        pass
