# coding: utf-8

from __future__ import unicode_literals, print_function, absolute_import, division


def group_by(key, iterable):
    res = {}

    for val in iterable:
        k = key(val)

        if k not in res:
            res[k] = []

        res[k].append(val)

    return res