from __future__ import unicode_literals, division, absolute_import

import sqlite3

import six
from six import itervalues


def text(string, encoding='utf8'):
    if isinstance(string, six.text_type):
        return string
    elif isinstance(string, six.binary_type):
        return string.decode(encoding)
    else:
        return six.text_type(string)


class BaseDB(object):
    __tablename__ = None
    placeholder = '%s'
    maxlimit = -1

    @staticmethod
    def escape(string):
        return '`%s`' % string

    @property
    def dbcur(self):
        raise NotImplementedError

    def _execute(self, sql_query, values=[]):
        dbcur = self.dbcur
        dbcur.execute(sql_query, values)
        return dbcur

    def _select(self, tablename=None, what="*", where="", where_values=[], offset=0, limit=None):
        tablename = self.escape(tablename or self.__tablename__)
        if isinstance(what, list) or isinstance(what, tuple) or what is None:
            what = ','.join(self.escape(f) for f in what) if what else '*'

        sql_query = "SELECT %s FROM %s" % (what, tablename)
        if where:
            sql_query += " WHERE %s" % where
        if limit:
            sql_query += " LIMIT %d, %d" % (offset, limit)
        elif offset:
            sql_query += " LIMIT %d, %d" % (offset, self.maxlimit)

        for row in self._execute(sql_query, where_values):
            yield row

    def _select2dic(self, tablename=None, what="*", where="", where_values=[],
                    order=None, offset=0, limit=None, group=None):
        tablename = self.escape(tablename or self.__tablename__)
        if isinstance(what, list) or isinstance(what, tuple) or what is None:
            what = ','.join(self.escape(f) for f in what) if what else '*'

        sql_query = "SELECT %s FROM %s" % (what, tablename)
        if where:
            sql_query += " WHERE %s" % where
        if group:
            sql_query += " GROUP BY %s" % group
        if order:
            sql_query += ' ORDER BY %s' % order
        if limit:
            sql_query += " LIMIT %d, %d" % (offset, limit)
        elif offset:
            sql_query += " LIMIT %d, %d" % (offset, self.maxlimit)

        dbcur = self._execute(sql_query, where_values)

        fields = [text(f[0]) for f in dbcur.description]

        for row in dbcur:
            yield dict(zip(fields, row))

    def _replace(self, tablename=None, **values):
        tablename = self.escape(tablename or self.__tablename__)
        if values:
            _keys = ", ".join(self.escape(k) for k in values)
            _values = ", ".join([self.placeholder, ] * len(values))
            sql_query = "REPLACE INTO %s (%s) VALUES (%s)" % (tablename, _keys, _values)
        else:
            sql_query = "REPLACE INTO %s DEFAULT VALUES" % tablename

        if values:
            dbcur = self._execute(sql_query, list(itervalues(values)))
        else:
            dbcur = self._execute(sql_query)
        return dbcur.lastrowid

    def _insert(self, tablename=None, **values):
        tablename = self.escape(tablename or self.__tablename__)
        if values:
            _keys = ", ".join((self.escape(k) for k in values))
            _values = ", ".join([self.placeholder, ] * len(values))
            sql_query = "INSERT INTO %s (%s) VALUES (%s)" % (tablename, _keys, _values)
        else:
            sql_query = "INSERT INTO %s DEFAULT VALUES" % tablename

        if values:
            dbcur = self._execute(sql_query, list(itervalues(values)))
        else:
            dbcur = self._execute(sql_query)
        return dbcur.lastrowid

    def _insertorreplace(self, tablename=None, **values):
        tablename = self.escape(tablename or self.__tablename__)
        if values:
            _keys = ", ".join((self.escape(k) for k in values))
            _values = ", ".join([self.placeholder, ] * len(values))
            sql_query = "INSERT OR REPLACE INTO %s (%s) VALUES (%s)" % (tablename, _keys, _values)
        else:
            sql_query = "INSERT OR REPLACE INTO %s DEFAULT VALUES" % tablename

        if values:
            dbcur = self._execute(sql_query, list(itervalues(values)))
        else:
            dbcur = self._execute(sql_query)
        return dbcur.lastrowid

    def _update(self, tablename=None, where="1=0", where_values=[], **values):
        tablename = self.escape(tablename or self.__tablename__)
        _key_values = ", ".join([
            "%s = %s" % (self.escape(k), self.placeholder) for k in values
        ])
        sql_query = "UPDATE %s SET %s WHERE %s" % (tablename, _key_values, where)

        return self._execute(sql_query, list(itervalues(values)) + list(where_values))

    def _delete(self, tablename=None, where="1=0", where_values=[]):
        tablename = self.escape(tablename or self.__tablename__)
        sql_query = "DELETE FROM %s" % tablename
        if where:
            sql_query += " WHERE %s" % where

        return self._execute(sql_query, where_values)


class DB(BaseDB):
    __tablename__ = "scraper_craigslist"
    __tablename2__ = "scraper_archive"
    __tablename3__ = "scraper_setting"
    __tablename4__ = "keyword_filter"
    placeholder = "?"

    def __init__(self):
        self.conn = sqlite3.connect("scraper.db")
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                '''CREATE TABLE `%s` (id INTEGER PRIMARY KEY AUTOINCREMENT, outid INT NOT NULL UNIQUE, url VARCHAR(255) NOT NULL, title VARCHAR(255) NOT NULL, location VARCHAR(255) NOT NULL, thumbnail TEXT, created INT NOT NULL, keyword VARCHAR(255) NOT NULL, comments TEXT, source VARCHAR(255) NOT NULL, is_delete INT DEFAULT 0, is_archive INT DEFAULT 0, is_save INT DEFAULT 0)''' % self.__tablename__
            )
        except:
            pass
        try:
            cursor.execute(
                '''CREATE TABLE `%s` (id INTEGER PRIMARY KEY AUTOINCREMENT, outid INT NOT NULL UNIQUE, url VARCHAR(255) NOT NULL, title VARCHAR(255) NOT NULL, location VARCHAR(255) NOT NULL, thumbnail TEXT, created INT NOT NULL, keyword VARCHAR(255) NOT NULL, comments TEXT, source VARCHAR(255) NOT NULL)''' % self.__tablename2__
            )
        except Exception:
            pass

        try:
            cursor.execute(
                '''CREATE TABLE `%s` (id INTEGER PRIMARY KEY AUTOINCREMENT, active INT NOT NULL, url VARCHAR(255) NOT NULL, source VARCHAR(255) NOT NULL, spider_ip VARCHAR(255) NOT NULL, spider_status VARCHAR(255) NOT NULL, last_full_scan_time INT NOT NULL)''' % self.__tablename3__
            )
        except Exception:
            pass

        try:
            cursor.execute(
                '''CREATE TABLE `%s` (id INTEGER PRIMARY KEY AUTOINCREMENT, keywords VARCHAR(255) NOT NULL)''' % self.__tablename4__
            )
        except Exception:
            pass

    @property
    def dbcur(self):
        return self.conn.cursor()

    def commit(self):
        return self.conn.commit()
