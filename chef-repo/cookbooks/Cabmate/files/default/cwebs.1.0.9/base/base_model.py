# -*- coding: utf-8 -*-
from datetime import date
from datetime import time
from datetime import datetime
from dateutil import parser
from datetime import timedelta
from decimal import Decimal
import json


class BaseModel(object):
    _r = {}

    def __init__(self, **kwargs):
        self._r = {}
        for attr, value in kwargs.iteritems():
            if hasattr(self, attr):
                setattr(self, attr, value)

    def __getattr__(self, item):
        if item == '_r':
            return {}
        return self._r[item] if item in self._r else object.__getattribute__(self, item)

    def __iter__(self):
        for attr in list(set(self.__dir__() +
                         list(self.__dict__) +
                         [name for name in self.__class__.__dict__ if name[:1] != '_'])):
            yield attr

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    @classmethod
    def create(cls, row, **kwargs):
        obj = cls(**kwargs)
        for attr, value in row.items():
            attr = str(attr)
            try:
                if hasattr(obj, attr):
                    preprocess_method = getattr(obj, 'preprocess_' + attr) \
                        if hasattr(obj, 'preprocess_' + attr) else None
                    if callable(preprocess_method):
                        value = preprocess_method(value)
                    if not value and type(getattr(obj, attr)) == str:
                        value = ''
                    if not value and type(getattr(obj, attr)) == unicode:
                        value = u''
                    #cast to model property type
                    if value and type(getattr(obj, attr)) != type(value) and getattr(obj, attr) is not None:
                        if type(getattr(obj, attr)) is datetime:
                            value = parser.parse(value)
                        elif type(getattr(obj, attr)) is date:
                            value = parser.parse(value).date()
                        elif isinstance(value, timedelta):
                            value = (datetime.min + value).time()
                        elif type(getattr(obj, attr)) is time:
                            value = parser.parse(value).time()
                        elif type(getattr(obj, attr)) is Decimal:
                            value = Decimal(str(value or 0))
                        else:
                            value = type(getattr(obj, attr))(value)
                    setattr(obj, attr, value)
                else:
                    obj._r[attr] = value
            except Exception as e:
                raise Exception('%s for \'%s\' attribute.' % (e.message, attr))
        return obj

    @staticmethod
    def format_string(value):
        return value and value.replace(u'\u2019', "'") or ''

    def __dir__(self):
        return []

    def to_api_dict(self):
        return dict((name, self.format_value(getattr(self, name))) for name in dir(self))
        #  if getattr(self, name) is not None

    def format_value(self, value):
        if value is None:
            return ''
        elif isinstance(value, BaseModel):
            return json.dumps(value.to_api_dict())
        elif isinstance(value, date):
            return value.isoformat()
        elif isinstance(value, time):
            return value.replace(microsecond=0).isoformat()
        elif isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, Decimal):
            return str(value)
        elif isinstance(value, list):
            return [i.to_api_dict() if isinstance(i, BaseModel) else str(i) for i in value]
        else:
            return value
