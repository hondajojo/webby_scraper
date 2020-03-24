# readme

```

pip install scrapy

cd webby_scraper/scraper

scrapy crawl craigslist_spider

```

then you will see data in `webby_scraper/scraper/scraper.db`

## setup new ubuntu server

```
sudo apt update && sudo apt install python3-pip -y && pip3 install scrapy feedparser
```



## start spider

```
cd /home/ubuntu/webby_scraper/scraper

# start rss spider
nohup python3 start_spider.py > /dev/null &

# start normal spider
nohup python3 start_normal_spider.py > /dev/null &
```

## stop spider
kill start_spider.py daemon or start_normal_spider.py daemon


## change url
~~edit /home/ubuntu/webby_scraper/url.ini~~


## reset data
login 104.156.49.114
```
cd /usr/local/src/webby_scraper/scraper

sqlite3 scraper.db

delete from scraper_craigslist;

```




TODO
---------------------------------

Web front-end & Web server
-----------------
1) Add comments field ✅
2) Add filter on the left : all, per keyword and then last filter is "spam" which got filtered ✅
3) Add save tick-box✅
4) Add delete tick-box (mark it for deletion and don't display it anymore) ✅
5) Add archive tick-box (it will save and hide the entry. compared to save which just saves it) ✅
6) Change the list to exclude entries marked for deletion ✅
7) Add notifications capability
8) web server back-end should purge anything not marked for save at midmight CDT each day. (To avoid the database getting to big)✅
9) Add a 2nd page called "archive"  ✅
        - a. This shows stuff which older than the current day 
        - b. has a search field to search old entries
        - c. Create a 2nd table or possibly even a 2nd database for this. This is poor man way to ensure that the current day database stays fast.

Back-end
-----------------
1) Add support for pulling RSS field instead of scraping✅
2) Convert crawler from script to daemon ✅
3) Add start/stop scripts for init 
4) Add round robin IP rotation
5) Add random user-agent rotation ✅
6) Add random referrer URL ✅
7) daemon should read to 2 ini format files:
        a. keywords file
        b. regions file ✅
8) keywords file has 2 properties: keyword and interval of how often to scrape
        Note: we may want to add a filters field to remove negative keywords
9) regions file is just a list of regions ✅



webby TODO(20190620)
----------------
1) Why is z1 test missing after many hours?
https://stlouis.craigslist.org/search/sss?query=z1&excats=20-102-2-39-5-22&sort=rel&postedToday=1✅

2) We need to refine search for each keyword
for example exclude cars for everything except corvette

3) Add notifications

4) Check why doesn't display correctly on iOS / the left side navigation is missing✅

5) Remove the word "keywords" from the left✅

6) Make links that have been visited purple✅

7) Setup 24 instances of crawler so that it scans 2x per second

8) Add some ban detection and alert us if crawler is having a problem

9) When you filter + paging may not be working correctly. Check for bugs✅

10) Bulk page operation.. how to delete a full page of results
