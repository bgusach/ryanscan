# coding: utf-8

from __future__ import unicode_literals, print_function, absolute_import, division


from datetime import datetime


def group_by(key, iterable):
    """
    Groups elements of iterable by a key function

    :rtype: dict

    """
    res = {}

    for val in iterable:
        k = key(val)

        if k not in res:
            res[k] = []

        res[k].append(val)

    return res


def parse_isodate(string):
    """
    Returns a datetime.date object for a string in the form YYYY-MM-DD

    :rtype: date

    """
    return datetime.strptime(string, '%Y-%m-%d').date()


class SoftDispatcher(object):
    """
    Wraps an object and delegates to it attribute access if attribute exists, otherwise returns a dummy function

    """

    def __init__(self, obj):
        self._obj = obj

    def dummy(*args, **kwargs):
        return None

    def __getattr__(self, item):
        return getattr(self._obj, item, self.dummy)
