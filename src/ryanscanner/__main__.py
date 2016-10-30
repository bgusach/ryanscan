# coding: utf-8

"""
Usage:
    ryanscanner search
    ryanscanner airports
    ryanscanner flights <origin> <destination> <start> <end>
"""

from __future__ import unicode_literals, absolute_import, print_function

from docopt import docopt


def main(args=None):
    args = docopt(__doc__, args)
    print(args)


if __name__ == '__main__':
    main()
