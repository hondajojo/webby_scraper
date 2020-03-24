import datetime
import six
import time

from scraper.basedb import DB


def get_day_time():
    day = datetime.datetime.now().strftime('%Y-%m-%d')
    return int(time.mktime(time.strptime(day, "%Y-%m-%d")))


def main():
    db = DB()
    for each in db._select2dic("scraper_craigslist", where="is_save = 1"):
        outid = each['outid']
        try:
            six.next(db._select2dic("scraper_archive", where="outid = ?", where_values=[outid]))
        except StopIteration:
            del each["id"]
            del each["is_delete"]
            del each["is_archive"]
            del each["is_save"]
            db._insert("scraper_archive", **each)
            db.commit()

    t = get_day_time()
    db._delete("scraper_craigslist", where="created <= ?", where_values=[t])
    db.commit()


if __name__ == '__main__':
    main()
