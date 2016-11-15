# coding: utf-8

"""
Usage:
    ryanscan find-airports [<terms>...]
    ryanscan find-flights <origins> <destinations> <earliest-to> <latest-to> [--max-flights=<max>] [--json]

Commands:
    find-airports               Output the list of all Ryanair airports with their IATA codes. Optionally accepts
                                any number of names to reduce the matches.

                                Example:
                                    ryanscan find-airports valencia

    find-flights                Given a list of origin airports (IATA codes separated by commas without spaces) and
                                a list of destination airports (same format as origins), and earliest and latest
                                dates for departure (format: YYYY-MM-DD), this command outputs a list of all found
                                solutions for the requested route.

                                Example:
                                    ryanscan find-flights BRE,HAM MAD,VLC 2016-10-10 2016-10-29

Options:
    --json                      Output results as JSON string to stdout
    -m --max-flights=<max>      Maximum flights to reach destination [default: 2]

"""

from __future__ import unicode_literals, absolute_import, print_function

import sys
import os
import json
import io
from docopt import docopt
from datetime import datetime
from decimal import Decimal

from . import core
from . import tools

try:
    input = raw_input
except NameError:
    pass


def find(origins, destinations, earliest_to, latest_to, max_flights, as_json=False):

    solutions = core.scan(
        origs=origins,
        dests=destinations,
        earliest_to=earliest_to,
        latest_to=latest_to,
        max_flights=max_flights,
    )

    if as_json:
        json.dump(make_jsonizable(solutions), fp=sys.stdout)
        return

    if not solutions:
        print('No flights found')

    for s in solutions:
        if len(s.flights) == 1:
            render_single_flight_solution(s)
            continue

        render_multiflight_solution(s)


def make_jsonizable(obj):
    if isinstance(obj, list):
        return [make_jsonizable(o) for o in obj]

    if isinstance(obj, datetime):
        return obj.isoformat()

    if isinstance(obj, Decimal):
        return float(obj)

    if isinstance(obj, (core.Solution, core.Flight)):
        obj = obj._asdict()

    if isinstance(obj, dict):
        obj = {k: make_jsonizable(v) for k, v in obj.items()}

    return obj


def main(args=None):
    try:
        _main(args)
    except core.AppError as exc:
        tools.log_info(exc.msg)

        log_path = os.path.join(os.path.expanduser('$'), 'ryanscan.error')

        with io.open(log_path, 'w', encoding='utf-8') as f:
            f.write(exc.msg)
            f.write(exc.details)

        return -1


def find_airports(terms):
    terms = [t.lower() for t in terms]

    def predicate(x):
        if not terms:
            return True

        x = x.lower()

        return any(t in x for t in terms)

    airports = [
        ('{name} ({country})'.format(**data), iata)
        for iata, data in core.get_airports().items()
        if any(predicate(x) for x in data.values())
    ]

    longest_key = max(len(airport[0]) for airport in airports)

    for airport in sorted(airports, key=lambda x: x[0]):
        print('%s: %s' % (airport[0].ljust(longest_key), airport[1]))

    return


def _main(args):
    args = docopt(__doc__, args)

    if args['find-flights']:
        find(
            origins=args['<origins>'].upper().split(','),
            destinations=args['<destinations>'].upper().split(','),
            earliest_to=tools.parse_isodate(args['<earliest-to>']),
            latest_to=tools.parse_isodate(args['<latest-to>']),
            max_flights=int(args['--max-flights']),
            as_json=args['--json'],
        )
        return

    if args['find-airports']:
        find_airports(terms=args['<terms>'])


def render_single_flight_solution(sol):
    print(format_flight(sol.flights[0]))


def format_flight(flight):
    return '{f.orig} > {f.dest} | {date} | {f.flight_number} | {f.price:.2f}€'.format(
        f=flight,
        date=format_date_pair(flight.date_out, flight.date_in),
    )


def render_multiflight_solution(sol):
    print('{s.orig} > {s.dest} | {dates} | {s.price:.2f}€'.format(s=sol, dates=format_date_pair(sol.date_out, sol.date_in)))

    for f in sol.flights:
        print('  - %s' % format_flight(f))


def format_date_pair(date_out, date_in):
    """
    :type date_out: datetime.datetime

    """
    full_format = '%a %Y-%m-%d %H:%M'
    only_time = '%H:%M'

    return '%s - %s' % (
        date_out.strftime(full_format),
        date_in.strftime(only_time if date_out.date() == date_in.date() else full_format),
    )

if __name__ == '__main__':
    sys.exit(main())
