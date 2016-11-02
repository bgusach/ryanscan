# coding: utf-8

from __future__ import unicode_literals, division, absolute_import, print_function

import itertools
from collections import namedtuple
from datetime import datetime
from datetime import time
from datetime import timedelta
from math import ceil
import requests as r
import decimal

from .tools import group_by
from .tools import SoftDispatcher


Flight = namedtuple('Flight', ['orig', 'dest', 'date_out', 'date_in', 'price', 'flight_number'])
DateInterval = namedtuple('DateInterval', ['start', 'end'])
BackendRequest = namedtuple('BackedRequest', ['orig', 'dest', 'date_to', 'date_back'])
Edge = namedtuple('Edge', ['orig', 'dest'])
Solution = namedtuple('Solution', ['orig', 'dest', 'date_out', 'date_in', 'flights', 'price'])
DateConstraint = namedtuple(
    'DateConstraint',
    ['earliest_out', 'latest_in', 'latest_out', 'min_between_flights', 'max_between_flights']
)


float2decimal = decimal.Context(prec=2, rounding=decimal.ROUND_HALF_DOWN).create_decimal_from_float


def make_solution(flights):
    # TODO [bgusach 29.10.2016]: handle no flights
    first = flights[0]
    last = flights[-1]

    return Solution(
        orig=first.orig,
        dest=last.dest,
        flights=list(flights),
        date_out=first.date_out,
        date_in=last.date_in,
        price=sum(f.price for f in flights),
    )


def get_airport_connections():
    return get_connections_from_stations_data(get_airports_raw_data())


def get_airports_raw_data():
    return get_json('https://api.ryanair.com/aggregate/3/common?embedded=airports&market=en-ie')


def get_json(path, **kwargs):
    print('Requesting: %s' % path)
    data = r.get(path, **kwargs).json()

    # pprint(data, indent=2)

    return data


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


def find_paths(origs, targets, network, max_flights=2):
    """
    :param origs: list of iata codes of aiports to start from
    :param targets: list of iata codes of destination airports
    :param dict network: graph of airports and routes
    :param int max_flights: desired max amount of flights

    """
    targets = set(targets)
    visited_nodes = set(origs)

    for orig in origs:
        for path in _find_path_for_origin(orig, targets, network, visited_nodes=visited_nodes, max_flights=max_flights):
            yield path


def _find_path_for_origin(orig, targets, network, explored_path=None, visited_nodes=None, max_flights=2):
    """
    :param str orig: origin airport
    :param set of str targets: possible destination airports
    :param dict network:
    :param list explored_path: list of edges already explored
    :param set of str visited_nodes: airports already visited (or that does not make any sense to fly to)
    :param int max_flights: max amount of flights

    """
    if explored_path is None:
        explored_path = []

    if visited_nodes is None:
        visited_nodes = set()

    if len(explored_path) < max_flights:
        destinations = network[orig]

        for dest in destinations & targets:
            yield explored_path + [Edge(orig, dest)]

        possible_intermediate_nodes = (destinations - targets) - visited_nodes
        this_visited_nodes = set_assoc(visited_nodes, orig)

        for node in possible_intermediate_nodes:
            for path in _find_path_for_origin(
                node,
                targets,
                network,
                explored_path + [Edge(orig, node)],
                this_visited_nodes,
                max_flights
            ):
                yield path

std_min_between_flights = timedelta(hours=1)
std_max_between_flights = timedelta(hours=5)


def get_solutions(
    paths,

    # TODO [bgusach 01.11.2016]: just pass a constraint named tuple
    dates_to,
    dates_back=None,
    min_between_flights=std_min_between_flights,
    max_between_flights=std_max_between_flights,
):
    # TODO [bgusach 01.11.2016]: inject these functions
    needed_requests = calculate_needed_requests(paths, dates_to, dates_back)

    edge2flights = group_by(
        lambda x: (x.orig, x.dest),
        (flight for req in needed_requests for flight in execute_request(req)),
    )

    earliest_out = datetime.combine(dates_to.start, time(0, 0, 0))
    latest_in = datetime.combine(dates_to.end, time(23, 59, 59))

    date_constraint = DateConstraint(
        earliest_out=earliest_out,
        latest_out=latest_in,
        latest_in=latest_in,
        min_between_flights=min_between_flights,
        max_between_flights=max_between_flights,
    )

    for path in paths:
        for solution in get_path_solutions(
            path,
            edge2flights,
            date_constraint=date_constraint,
        ):
            yield solution


def are_flights_compatible(flights, date_constraint):
    """
    Return whether the collection of flights is consistent with itself, and with the date constraints

    :type flights: list of Flight
    :type date_constraint: DateConstraint
    :rtype: bool

    """
    if not flights:
        return True

    this_flight, rest = flights[0], flights[1:]

    if this_flight.date_in > date_constraint.latest_in:
        return False

    if this_flight.date_out < date_constraint.earliest_out or this_flight.date_out > date_constraint.latest_out:
        return False

    date_constraint = date_constraint._replace(
        earliest_out=this_flight.date_in + date_constraint.min_between_flights,
        latest_out=this_flight.date_in + date_constraint.max_between_flights,
    )

    return are_flights_compatible(rest, date_constraint)


def get_path_solutions(path, edge2flights, date_constraint, are_flights_compatible=are_flights_compatible):
    if not all(edge in edge2flights for edge in path):
        return []

    all_posible_solutions = itertools.product(*[edge2flights[edge] for edge in path])

    return [
        make_solution(s)
        for s in all_posible_solutions
        if s
        and are_flights_compatible(s, date_constraint)
    ]


def calculate_needed_requests(paths, dates_to, dates_back=None):
    # TODO [bgusach 17.10.2016]: handle dates_back
    start, end = dates_to
    week_intervals_to_query = int(ceil((end - start).days / 7)) or 1  # At least one we need
    dates_to_query = [start + timedelta(days=7 * x) for x in range(week_intervals_to_query)]

    return {
        BackendRequest(edge.orig, edge.dest, date, None)
        for path in paths
        for edge in path
        for date in dates_to_query
    }


def execute_request(request):
    query = {
        'ADT': 1,
        'CHD': 0,
        'DateOut': request.date_to.isoformat(),
        # 'DateOut': request.date_to.strftime(ISO_DATE_FORMAT),
        # 'DateIn': date.strftime(RAR_DATE_FORMAT),
        'Destination': request.dest,
        'FlexDaysOut': 6,
        'INF': 0,
        'Origin': request.orig,
        'RoundTrip': 'false',
        'TEEN': 0,
    }

    # FIXME [bgusach 30.10.2016]: add support for more countries/currencies
    res = get_json('https://desktopapps.ryanair.com/en-ie/availability', params=query)

    return [
        Flight(
            orig=trip['origin'],
            dest=trip['destination'],
            date_out=parse_full_date(flight['time'][0]),
            date_in=parse_full_date(flight['time'][1]),
            price=get_cheapest_fare_from_flight(flight),
            flight_number=flight['flightNumber'],
        )
        for trip in res['trips']
        for date in trip['dates']
        for flight in date['flights']
        if flight['faresLeft']
    ]


def get_cheapest_fare_from_flight(flight):
    fare = flight.get('regularFare') or flight.get('leisureFare') or flight['businessFare']
    return float2decimal(fare['fares'][0]['amount'])


def parse_full_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f')


def get_airports():
    return get_json('https://desktopapps.ryanair.com/en-ie/res/stations')


def scan(
    origs,
    dests,
    earliest_to,
    latest_to,
    listener=None,
    earliest_back=None,
    latest_back=None,
    max_flights=2,
    min_between_flights=std_min_between_flights,
    max_between_flights=std_max_between_flights,
    get_network=get_airport_connections,
    find_paths=find_paths
):
    """
    :param dests:
    :param datetime.date earliest_to: Earliest date to fly to destination
    :param datetime.date latest_to: Latest date to fly to destination
    :param datetime.date earliest_back: Earliest date to return
    :param datetime.date latest_back: Latest date to return
    :param int max_flights: Maximum number of flights allowed to reach a destination
    :param timedelta min_between_flights: Minimum time between flights
    :param timedelta max_between_flights: Maximum time between flights

    :return: list of Solution sorted by ascendant date

    """
    listener = SoftDispatcher(listener)
    listener.getting_network()
    network = get_network()

    listener.finding_paths()
    paths = list(find_paths(origs, dests, network, max_flights))
    listener.paths_found(paths)

    dates_to = DateInterval(earliest_to, latest_to)

    listener.finding_valid_solutions()
    solutions = get_solutions(paths, dates_to)

    return sorted(solutions, key=lambda s: s.date_out)

