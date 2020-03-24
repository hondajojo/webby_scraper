import os
from configparser import ConfigParser
from datetime import datetime


def parse_regions():
    e = os.path.abspath(os.path.join(__file__, "../../"))
    regions_file = os.path.join(e, "regions.ini")
    config = ConfigParser()
    config.read(regions_file)
    return config


REGIONS_LIST = parse_regions()


def get_pagination(**kwargs):
    from flask_paginate import Pagination

    kwargs.setdefault('record_name', 'records')
    return Pagination(css_framework="bootstrap4",
                      link_size="sm",
                      alignment="",
                      show_single_page=False,
                      **kwargs
                      )


def pretty_date(created):
    now = datetime.now()
    diff = now - datetime.fromtimestamp(created)
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(int(second_diff / 60)) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(int(second_diff / 3600)) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(int(day_diff / 7)) + " weeks ago"
    if day_diff < 365:
        return str(int(day_diff / 30)) + " months ago"
    return str(int(day_diff / 365)) + " years ago"
