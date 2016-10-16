# coding: utf-8

from __future__ import unicode_literals

from collections import namedtuple
from datetime import datetime
from datetime import timedelta
import json
from pprint import pprint


Flight = namedtuple('Flight', ['orig', 'dest', 'date0', 'date1', 'price'])
Solution = namedtuple('Solution', ['orig', 'dest', 'date0', 'date1', 'flights', 'price'])
DateInterval = namedtuple('DateInterval', ['start', 'end'])


def get_airport_connections():
    return get_connections_from_stations_data(get_airports_raw_data())


def get_airports_raw_data():
    with open('common.json') as f:
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
    pass


def scan(origs, dests, dates_to, dates_back, get_network=get_airport_connections, find_paths=find_paths):
    network = get_network()

    for x in find_paths({'BRE'}, {'VLC', 'ALC'}, network):
        print(x)


if __name__ == '__main__':
    scan(0, 0, 0, 0)
