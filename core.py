# coding: utf-8

from __future__ import unicode_literals, division, absolute_import

import requests as r
from collections import namedtuple
from datetime import datetime
from itertools import tee
from datetime import timedelta
from math import ceil
import json
from pprint import pprint


Flight = namedtuple('Flight', ['orig', 'dest', 'date0', 'date1', 'price', 'flight_number'])
Solution = namedtuple('Solution', ['orig', 'dest', 'date0', 'date1', 'flights', 'price'])
DateInterval = namedtuple('DateInterval', ['start', 'end'])
BackendRequest = namedtuple('BackedRequest', ['orig', 'dest', 'date_to', 'date_back'])


def get_airport_connections():
    return get_connections_from_stations_data(get_airports_raw_data())


def get_airports_raw_data():
    with open('test_data/common.json') as f:
        return json.load(f)


def get_airport_names_from_raw_data(data):
    return {a['iataCode']: a['name'] for a in data['airports']}


def get_connections_from_stations_data(data):
    return {
        airport['iataCode']: {
            item.partition(':')[2]
            for item in airport['routes']
            if item.startswith('airport:')
        }
        for airport in data['airports']
    }


def set_assoc(s, val):
    """
    Returns a new set containing all elements of `s` plus the element `val`

    """
    res = s.copy()
    res.add(val)

    return res


def find_paths(origs, targets, network, explored_path=None, forbidden_nodes=None, max_flights=2):
    if max_flights < 1:
        raise ValueError('The amount of flights must be at least 1')

    if explored_path is None:
        explored_path = []

    if forbidden_nodes is None:
        forbidden_nodes = set()

    for orig in origs:
        this_explored_path = explored_path + [orig]

        destinations = network[orig]

        for dest in destinations & targets:
            yield this_explored_path + [dest]

        if len(this_explored_path) == max_flights:
            continue

        possible_nodes = (destinations - targets) - forbidden_nodes
        this_forbidden_nodes = set_assoc(forbidden_nodes, orig)

        for path in find_paths(possible_nodes, targets, network, this_explored_path, this_forbidden_nodes, max_flights):
            yield path


def get_prices(paths, dates_to, dates_back=None, min_transfer_time=timedelta(hours=1), max_transfer_time=timedelta(hours=5)):

    needed_requests = calculate_needed_requests(paths, dates_to, dates_back)

    segment2flights = group_by(
        lambda x: (x.orig, x.dest),
        (flight for req in needed_requests for flight in execute_request(req)),
    )

    pprint(segment2flights, indent=2)
    return

    solutions = []

    # extract into own recursive function
    for path in paths:
        # a > b > c
        for segment in get_segments_from_path(path):
            # a > b
            for flight in segment2flights[segment]:
                pass


def group_by(key, iterable):
    res = {}

    for val in iterable:
        k = key(val)

        if k not in res:
            res[k] = []

        res[k].append(val)

    return res


def calculate_needed_requests(paths, dates_to, dates_back=None):
    # TODO [bgusach 17.10.2016]: handle dates_back
    start, end = dates_to
    week_intervals_to_query = int(ceil((end - start).days / 7)) or 1  # At least one we need
    dates_to_query = [start + timedelta(days=7 * x) for x in range(week_intervals_to_query)]

    return {
        BackendRequest(segment[0], segment[1], date, None)
        for path in paths
        for segment in get_segments_from_path(path)
        for date in dates_to_query
    }


def execute_request(request):
    query = {
        'ADT': 1,
        'CHD': 0,
        'DateOut': request.date_to.strftime(RAR_DATE_FORMAT),
        # 'DateIn': date.strftime(RAR_DATE_FORMAT),
        'Destination': request.dest,
        'FlexDaysOut': 6,
        'INF': 0,
        'Origin': request.orig,
        'RoundTrip': 'false',
        'TEEN': 0,
    }

    res = r.get('https://desktopapps.ryanair.com/en-ie/availability', params=query).json()

    return [
        Flight(
            orig=trip['origin'],
            dest=trip['destination'],
            date0=parse_full_date(flight['time'][0]),
            date1=parse_full_date(flight['time'][1]),
            price=flight['regularFare']['fares'][0]['amount'],
            flight_number=flight['flightNumber'],
        )
        for trip in res['trips']
        for date in trip['dates']
        for flight in date['flights']
    ]


def parse_full_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f')

RAR_DATE_FORMAT = '%Y-%m-%d'


def get_segments_from_path(path):
    """
    Given a list of airports, it returns a list of each segment.
    From ['BRE', 'VLC', 'HAM'] --> [('BRE', 'VLC'), ('VLC', 'HAM')]

    """
    path1, path2 = tee(path)
    next(path2)

    return [tuple(p) for p in zip(path1, path2)]


def scan(origs, dests, dates_to, dates_back, get_network=get_airport_connections, find_paths=find_paths):
    network = get_network()

    paths = find_paths({'BRE'}, {'ALC'}, network, max_flights=1)
    prices = get_prices(paths, (datetime(2016, 11, 10), datetime(2016, 11, 15)))


if __name__ == '__main__':
    scan(0, 0, 0, 0)
