# coding: utf-8

"""
Usage:
    pyanair.py airports
    pyanair.py flights <origin> <destination> <start> <end>
"""

from __future__ import unicode_literals

import sys
import requests as r
from datetime import datetime
from collections import defaultdict
from docopt import docopt


def parse_full_date(date):
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')


def parse_simple_date(date):
    return datetime.strptime(date, EASY_DATE_FORMAT)


def format_time(date):
    return date.strftime('%H:%M')


EASY_DATE_FORMAT = '%d-%m-%Y'
RAR_DATE_FORMAT = '%Y-%m-%d'



def process_data(data):
    res = {
        'currency': data['currency'],
        'flights': defaultdict(list)
    }

    for trip in data['trips']:
        orig = trip['origin']
        dest = trip['destination']

        res['flights'].append({
            ''
        })

    return {
        'currency': data['currency'],
        'flights': {
        }
    }


def query_flight_info(orig, dest, date):
    query = {
        'ADT': '1',
        'CHD': '0',
        'DateOut': date.strftime(RAR_DATE_FORMAT),
        'Destination': dest,
        'FlexDaysOut': '4',
        'INF': '0',
        'Origin': orig,
        'RoundTrip': 'false',
        'TEEN': '0',
    }

    # print(query)

    return r.get('https://desktopapps.ryanair.com/en-ie/availability', params=query).json()

    import json
    with open('lol.json') as f:
        res = json.load(f)

    return res

def main(origins, destinations, start, end):
    for orig in origins:
        for dest in destinations:
            if orig == dest:
                continue

            data = query_flight_info(orig, dest, start)

            print('%s > %s' % (orig, dest))
            for date in data['trips'][0]['dates']:
                if not date['flights']:
                    continue

                this_date = parse_full_date(date['dateOut'])

                print('  - ' + this_date.strftime('%a ' + EASY_DATE_FORMAT))

                for flight in date['flights']:
                    departure, arrival = map(parse_full_date, flight['time'])

                    print('    - {departure} > {arrival} | {price}{currency}'.format(
                        departure=format_time(departure),
                        arrival=format_time(arrival),
                        price=flight['regularFare']['fares'][0]['amount'],
                        currency=data['currency']
                    ))


if __name__ == '__main__':
    converters = {
        '<origin>': lambda x: x.split(','),
        '<destination>': lambda x: x.split(','),
        '<start>': parse_simple_date,
        # '<end>': parse_simple_date,
    }

    args = {k: converters.get(k, str)(v) for k, v in docopt(__doc__).items()}

    # main(args['<origin>'], args['<destination>'], args['<start>'], args['<end>'])
    # https://desktopapps.ryanair.com/en-ie/res/stations

    import json
    with open('common.json') as f:
        raw_data = json.load(f)

    connections = get_connections(raw_data)

    import pprint
    pprint.pprint(connections)
