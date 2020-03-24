#!/bin/sh
export PATH=$PATH:/usr/local/bin
cd /usr/local/src/webby_scraper/scraper
nohup python pure_database.py >>pure_database.log 2>&1