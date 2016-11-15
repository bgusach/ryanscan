# coding: utf-8

from __future__ import unicode_literals, print_function, absolute_import, division

import sys
from datetime import datetime
import decimal


def log_info(msg):
    print('ryanscan: %s' % msg, file=sys.stderr)


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


float2decimal = decimal.Context(prec=2, rounding=decimal.ROUND_HALF_DOWN).create_decimal_from_float


def set_assoc(s, val):
    """
    Returns a new set containing all elements of `s` plus the element `val`

    """
    res = s.copy()
    res.add(val)

    return res