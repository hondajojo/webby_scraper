import datetime
import time

import six
from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
from flask_paginate import get_page_args
from six.moves.urllib.parse import urlparse, parse_qs

from form import AddConfigForm, AddKeywordsFilterForm
from scraper.basedb import DB
from utils import pretty_date, get_pagination

app = Flask(__name__)

app.config['SECRET_KEY'] = 'hard to guess'
app.config['per_page'] = 100


@app.route("/")
def index():
    keyword = request.args.get("keyword", "")
    page = request.args.get("page", 1, type=int)
    offset = (page - 1) * 100
    # page, per_page, offset = get_page_args(page_parameter='page',
    #                                        per_page_parameter='per_page')
    db = DB()

    total = 0
    if keyword:
        rr = db._execute(
            "select count(1) from scraper_craigslist where keyword = ? and is_delete = 0 and is_archive = 0",
            values=[keyword])
        for row in rr:
            total = row[0]

        session_list = db._select2dic("scraper_craigslist", where="keyword = ? and is_delete = 0 and is_archive = 0",
                                      where_values=[keyword],
                                      order="created desc", limit=100, offset=offset)
    else:
        rr = db._execute(
            "select count(1) from scraper_craigslist where keyword is not null and is_delete = 0 and is_archive = 0")
        for row in rr:
            total = row[0]
        session_list = db._select2dic("scraper_craigslist",
                                      where="keyword is not null and is_delete = 0 and is_archive = 0",
                                      order="created desc", limit=100, offset=offset)
    pagination = get_pagination(page=page,
                                per_page=100,
                                total=total,
                                record_name='users',
                                format_total=True,
                                format_number=True,
                                )
    data = []
    for each in session_list:
        each['created'] = pretty_date(int(each['created']))
        data.append(each)
    return render_template("list2.html", session_list=data, keyword=keyword, pagination=pagination, page=page)


@app.route("/archive_list")
def archive_list():
    keyword = request.args.get("keyword", "")
    db = DB()
    if keyword:
        session_list = db._select2dic("scraper_archive",
                                      where_values=[keyword],
                                      order="created desc")
    else:
        session_list = db._select2dic("scraper_archive", order="created desc")
    data = []
    for each in session_list:
        each['created'] = pretty_date(int(each['created']))
        data.append(each)
    return render_template("archive_list.html", session_list=data, keyword=keyword)


@app.route("/keyword_filter", methods=["GET", "POST"])
def keyword_filter():
    form = AddKeywordsFilterForm()
    db = DB()
    ret = None
    try:
        ret = six.next(db._select2dic("keyword_filter"))
    except:
        pass
    if form.validate_on_submit():
        keywords = form.keywords.data
        if ret:
            db._update("keyword_filter", where="id = ?", where_values=[ret['id']], keywords=keywords)
            db.commit()
            return render_template("keyword_filter.html", form=form)
        else:
            db._insert("keyword_filter", **{"keywords": keywords})
            db.commit()
            return redirect(url_for("keyword_filter"))
    else:
        flash_errors(form)

    if ret:
        form.keywords.data = ret['keywords']
    return render_template("keyword_filter.html", form=form)


@app.route("/getdata")
def getdata():
    keyword = request.args.get("keyword")
    db = DB()
    if keyword:
        session_list = db._select2dic("scraper_craigslist", where="keyword = ? and is_delete = 0 and is_archive = 0",
                                      where_values=[keyword],
                                      order="created desc", limit=100, offset=0)
    else:
        session_list = db._select2dic("scraper_craigslist",
                                      where="keyword is not null and is_delete = 0 and is_archive = 0",
                                      order="created desc", limit=100, offset=0)
    data = []
    for each in session_list:
        each['created'] = pretty_date(int(each['created']))
        data.append(each)
    html = []
    for each in data:
        item_html = '''
        <tr>
            <td>%s</td>
            <td>%s</td>
            <td><a id="outurl" href="%s" target="_blank">%s</a></td>
            <td>%s</td>
            <td><input id="comments" name="comments" size="30" type="text" data-id="%s" value="%s"></td>
            <td>%s</td>
            <td>
                <a href="#" id="delete" data-id="%s">delete</a>
                <a href="#" id="archive" data-id="%s">archive</a>
                <a href="#" id="save" data-id="%s">save</a>
            </td>
        </tr>
        ''' % (
            each['keyword'], each['source'], each['url'], each['title'], each['location'], each['id'],
            each['comments'] if each['comments'] else "",
            each['created'], each['id'], each['id'], each['id'])
        html.append(item_html)
    return jsonify({"html": ''.join(html)})


@app.route("/getsettings")
def getsettings():
    db = DB()
    configs = list()
    for each in db._select2dic("scraper_setting", order="id desc"):
        active_status = "active"
        if each['active'] == 0:
            active_status = "inactive"
        each['active_status'] = active_status
        configs.append(each)
    html = []
    for each in configs:
        item_html = '''
        <tr>
            <td>%s</td>
            <td>%s<br><a id="switch" href="#" data-id="%s"
                                                    data-active="%s">Switch</a></td>
            <td>%s</td>
            <td>
                <a href="/deleteconfig?id=%s">delete</a>
                <a href="/editconfig?id=%s">edit</a>
            </td>
            <td>%s</td>

        </tr>
        ''' % (each['source'], each['active_status'], each['id'], each['active'], each['spider_ip'], each['id'],
               each['id'], each['url'])
        html.append(item_html)
    return jsonify({"html": ''.join(html)})


@app.route("/delete")
def delete():
    id = request.args.get("id", type=int)
    if id:
        db = DB()
        try:
            six.next(db._select2dic("scraper_craigslist", where="id = ?", where_values=[id]))
        except StopIteration:
            return jsonify({"code": 404, "message": "not found", "data": None})
        db._delete("scraper_craigslist", where="id = ?", where_values=[id])
        db.commit()
        return jsonify({"code": 200, "message": "success", "data": None})
    return jsonify({"code": 500, "message": "missing id", "data": None})


@app.route("/delete_archive")
def delete_archive():
    id = request.args.get("id", type=int)
    if id:
        db = DB()
        try:
            six.next(db._select2dic("scraper_archive", where="id = ?", where_values=[id]))
        except StopIteration:
            return jsonify({"code": 404, "message": "not found", "data": None})
        db._delete("scraper_archive", where="id = ?", where_values=[id])
        db.commit()
        return jsonify({"code": 200, "message": "success", "data": None})
    return jsonify({"code": 500, "message": "missing id", "data": None})


@app.route("/archive")
def archive():
    id = request.args.get("id", type=int)
    if id:
        db = DB()
        try:
            ret = six.next(db._select2dic("scraper_craigslist", where="id = ?", where_values=[id]))
            db._delete("scraper_craigslist", where="id = ?", where_values=[id])
            db.commit()
        except StopIteration:
            return jsonify({"code": 404, "message": "not found", "data": None})
        del ret["id"]
        del ret["is_delete"]
        del ret["is_archive"]
        del ret["is_save"]
        db._insert("scraper_archive", **ret)
        db.commit()
        return jsonify({"code": 200, "message": "success", "data": None})
    return jsonify({"code": 500, "message": "missing id", "data": None})


@app.route("/save")
def save():
    id = request.args.get("id", type=int)
    if id:
        db = DB()
        try:
            six.next(db._select2dic("scraper_craigslist", where="id = ?", where_values=[id]))
        except StopIteration:
            return jsonify({"code": 404, "message": "not found", "data": None})
        db._update("scraper_craigslist", where="id = ?", where_values=[id], is_save=1)
        db.commit()
        return jsonify({"code": 200, "message": "success", "data": None})
    return jsonify({"code": 500, "message": "missing id", "data": None})


@app.route("/addcomment", methods=["POST"])
def addcomment():
    id = request.form["id"]
    comment = request.form["comment"]
    if id:
        db = DB()
        try:
            six.next(db._select2dic("scraper_craigslist", where="id = ?", where_values=[id]))
        except StopIteration:
            return jsonify({"code": 404, "message": "not found", "data": None})
        db._update("scraper_craigslist", where="id = ?", where_values=[id], comments=comment)
        db.commit()
        return jsonify({"code": 200, "message": "success", "data": None})
    return jsonify({"code": 500, "message": "missing id", "data": None})


@app.route("/adddata", methods=["POST"])
def adddata():
    outid = request.form["outid"]
    url = request.form["url"]
    title = request.form["title"]
    source = request.form.get('source', 'craigslist')
    location = request.form["location"]
    thumbnail = request.form["thumbnail"]
    keyword = request.form["keyword"]
    created = request.form["created"]
    if outid and url and title and keyword and created and source:
        db = DB()
        try:
            six.next(
                db._select2dic("scraper_craigslist", where="outid = ? and source = ?", where_values=[outid, source]))
            return jsonify({"code": 303, "message": "data exists", "data": {'url': url, 'outid': outid}})
        except StopIteration:
            db._insert("scraper_craigslist",
                       **{"outid": outid, "url": url, "title": title, 'location': location, 'thumbnail': thumbnail,
                          'keyword': keyword, 'created': created, 'is_delete': 0, 'is_archive': 0, 'is_save': 0,
                          'source': source})
            db.commit()
            return jsonify({"code": 200, "message": "success", "data": None})
    return jsonify({"code": 500, "message": "missing params", "data": None})


@app.route("/spider_status", methods=["POST"])
def spider_status():
    id = request.form["id"]
    status = request.form["status"]

    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr

    if id and status:
        db = DB()
        try:
            six.next(
                db._select2dic("scraper_setting", where="id = ?", where_values=[id]))
            if status == "Sleeping":
                db._update("scraper_setting", where="spider_ip = ?", where_values=[ip], spider_status=status,
                           last_full_scan_time=int(time.mktime(time.gmtime())))
            else:
                db._update("scraper_setting", where="spider_ip = ?", where_values=[ip], spider_status=status)
            db.commit()
            return jsonify({"code": 200, "message": "success", "data": None})
        except StopIteration:
            return jsonify({"code": 404, "message": "not found", "data": None})
    return jsonify({"code": 500, "message": "missing params", "data": None})


@app.route("/addsetting", methods=["GET", "POST"])
def addconfig():
    form = AddConfigForm()
    form.active.data = "0"
    if form.validate_on_submit():
        # spider_ip = form.spider_ip.data
        url = form.url.data
        active = form.active.data
        source = form.source.data
        db = DB()

        try:
            six.next(db._select2dic("scraper_setting", where="url = ? and source = ?",
                                    where_values=[url, source]))
            form.url.errors.append("url exists")
            flash_errors(form)
            return render_template("addconfig.html", form=form)
        except StopIteration:
            db._insert("scraper_setting", **{"spider_ip": "", "url": url, "active": active, "source": source})
            db.commit()
            return redirect(url_for("configlist"))
    else:
        flash_errors(form)
    return render_template("addconfig.html", form=form)


@app.route("/settings", methods=["GET", "POST"])
def configlist():
    db = DB()
    configs = list()
    for each in db._select2dic("scraper_setting", order="id desc"):
        active_status = "active"
        if each['active'] == 0:
            active_status = "inactive"
        each['active_status'] = active_status
        configs.append(each)
    return render_template("configlist.html", configs=configs)


@app.route("/serverstatus", methods=["GET", "POST"])
def serverstatus():
    db = DB()
    configs = list()
    config_dict = dict()
    for each in db._select2dic("scraper_setting",
                               where="spider_ip is not null and spider_ip != '' and spider_status != ''"):
        if each['last_full_scan_time'] > 0:
            each['last_full_scan_time'] = datetime.datetime.fromtimestamp(each['last_full_scan_time']).strftime(
                '%Y-%m-%d %H:%M:%S')
        url = each['url']
        if url:
            if 'craigslist' in url:
                keyword = parse_qs(urlparse(url).query)['query'][0].split('-')[0].strip()
            elif 'kijiji' in url:
                keyword = urlparse(url).path.split('/')[3].strip()
            else:
                keyword = parse_qs(urlparse(url).query)['_nkw'][0].strip()
        else:
            keyword = ""
        each['keyword'] = keyword
        configs.append(each)
        spider_ip = each['spider_ip']
        if config_dict.get(spider_ip):
            config_dict[spider_ip]['keyword'].append(keyword)
            config_dict[spider_ip]['spider_status'] = each['spider_status']
            config_dict[spider_ip]['last_full_scan_time'] = each['last_full_scan_time']
        else:
            config_dict[spider_ip] = {"keyword": [keyword], 'spider_status': each['spider_status'],
                                      'last_full_scan_time': each['last_full_scan_time']}

    for k, v in config_dict.items():
        v['keyword'] = ', '.join(v['keyword'])

    return render_template("serverstatus.html", configs=configs, config_dict=config_dict)


@app.route("/getserverstatus", methods=["GET", "POST"])
def getserverstatus():
    db = DB()
    configs = list()
    config_dict = dict()
    for each in db._select2dic("scraper_setting",
                               where="spider_ip is not null and spider_ip != '' and spider_status != ''"):
        if each['last_full_scan_time'] > 0:
            each['last_full_scan_time'] = datetime.datetime.fromtimestamp(each['last_full_scan_time']).strftime(
                '%Y-%m-%d %H:%M:%S')
        url = each['url']
        if url:
            if 'craigslist' in url:
                keyword = parse_qs(urlparse(url).query)['query'][0].split('-')[0].strip()
            elif 'kijiji' in url:
                keyword = urlparse(url).path.split('/')[3].strip()
            else:
                keyword = parse_qs(urlparse(url).query)['_nkw'][0].strip()
        else:
            keyword = ""
        each['keyword'] = keyword
        configs.append(each)
        spider_ip = each['spider_ip']
        if config_dict.get(spider_ip):
            config_dict[spider_ip]['keyword'].append(keyword)
            config_dict[spider_ip]['spider_status'] = each['spider_status']
            config_dict[spider_ip]['last_full_scan_time'] = each['last_full_scan_time']
        else:
            config_dict[spider_ip] = {"keyword": [keyword], 'spider_status': each['spider_status'],
                                      'last_full_scan_time': each['last_full_scan_time']}

    for k, v in config_dict.items():
        v['keyword'] = ', '.join(v['keyword'])

    html = []
    for k, v in config_dict.items():
        item_html = '''
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            ''' % (k, v['keyword'], v['spider_status'], v['last_full_scan_time'])
        html.append(item_html)
    return jsonify({"html": ''.join(html)})


@app.route("/statusswitch", methods=["GET", "POST"])
def statusswitch():
    id = request.args.get("id", type=int)
    active = request.args.get("active", type=int)
    if id and active is not None:
        db = DB()
        try:
            active = 0 if active == 1 else 1
            ret = six.next(db._select2dic("scraper_setting", where="id = ?", where_values=[id]))

            if int(active) == 0:
                db._update("scraper_setting", where="id=?", where_values=[id], active=active, spider_ip="")
            else:
                db._update("scraper_setting", where="id = ?", where_values=[id], active=active)
            ret['active'] = active
            ret['spider_ip'] = "" if active == 0 else ret['spider_ip']
            db.commit()
            active_status = "inactive" if ret['active'] == 0 else "active"
            ret['active_status'] = active_status

            html = """
            <td>%s</td>
            <td>%s<br><a id="switch" href="#" data-id="%s" data-active="%s">Switch</a></td>
            <td>%s</td>
            <td>
                <a href="/deleteconfig?id=%s">delete</a>
                <a href="/editconfig?id=%s">edit</a>
            </td>
            <td>%s</td>
            """ % (
                ret['source'], ret["active_status"], ret['id'], ret['active'], ret['spider_ip'],
                ret['id'], ret['id'], ret["url"],)

            return jsonify({"code": 200, "message": "success", "data": html})
        except StopIteration:
            return jsonify({"code": 404, "message": "not found", "data": None})
    return jsonify({"code": 500, "message": "missing id", "data": None})


@app.route("/spider_config", methods=["GET", "POST"])
def getconfig():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    sources = ["craigslist", "ebay", "kijiji", "facebook"]
    db = DB()
    data = []
    for source in sources:
        try:
            ret = six.next(
                db._select2dic("scraper_setting", where="source = ? and spider_ip = ? and active = 1",
                               where_values=[source, ip]))
            url = ret['url']
            id = ret['id']

        except:
            try:
                ret = six.next(
                    db._select2dic("scraper_setting", where="source = ? and active = 0", where_values=[source]))
                url = ret['url']
                id = ret['id']
                db._update("scraper_setting", where="id = ?", where_values=[id], active=1, spider_ip=ip)
                db.commit()
            except StopIteration:
                url = ""
                id = 0

        data.append({
            "url": url,
            "source": source,
            "id": id,
        })
    return jsonify(data), 200


@app.route("/deleteconfig", methods=["GET", "POST"])
def deleteconfig():
    id = request.args.get("id", type=int)
    if id:
        db = DB()
        try:
            six.next(db._select2dic("scraper_setting", where="id = ?", where_values=[id]))
            db._delete("scraper_setting", where="id = ?", where_values=[id])
            db.commit()
            return redirect(url_for("configlist"))
        except StopIteration:
            return redirect(url_for("configlist"))
    return redirect(url_for("configlist"))


@app.route("/editconfig", methods=["GET", "POST"])
def editconfig():
    id = request.args.get("id", type=int)
    if id:
        db = DB()
        try:
            ret = six.next(db._select2dic("scraper_setting", where="id = ?", where_values=[id]))
            form = AddConfigForm()

            if form.validate_on_submit():
                # spider_ip = form.spider_ip.data
                url = form.url.data
                active = form.active.data
                source = form.source.data
                if int(active) == 0:
                    db._update("scraper_setting", where="id=?", where_values=[id], source=source, url=url,
                               active=active, spider_ip="")
                else:
                    db._update("scraper_setting", where="id=?", where_values=[id], source=source, url=url,
                               active=active)
                db.commit()
                return redirect(url_for("configlist"))
            else:
                flash_errors(form)
            form.source.data = ret['source']
            # form.spider_ip.data = ret['spider_ip']
            form.url.data = ret['url']
            form.active.data = str(ret['active'])
            return render_template("addconfig.html", form=form)
        except StopIteration:
            return redirect(url_for("configlist"))
    return redirect(url_for("configlist"))


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u'%s - %s' % (getattr(form, field).label.text, error), 'error')


@app.context_processor
def utility_processor():
    injections = dict()

    def get_keywords():
        db = DB()
        keywords = []
        for each in db._select2dic("scraper_craigslist", group="keyword", what=["keyword"]):
            keyword = each["keyword"]
            if keyword:
                keywords.append(keyword)
        return keywords

    injections.update(get_keywords=get_keywords)
    return injections


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
