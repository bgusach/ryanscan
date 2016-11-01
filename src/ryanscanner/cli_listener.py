# coding: utf-8

from __future__ import unicode_literals, print_function, absolute_import


def getting_network():
    print('Getting airport network')


def finding_paths():
    print('Finding possible paths')


def paths_found(paths):
    print('Possible paths found:')

    for path in paths:
        print('  ' + ', '.join(['%s > %s' % edge for edge in path]))


def finding_valid_solutions():
    print('Finding valid solutions')
