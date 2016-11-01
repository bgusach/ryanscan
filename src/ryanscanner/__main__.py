# coding: utf-8

"""
Usage:
    ryanscanner search
    ryanscanner airports
    ryanscanner flights <origins> <destinations> <start> <end>
"""

from __future__ import unicode_literals, absolute_import, print_function

from docopt import docopt
from datetime import date

from . import core
from . import cli_listener


def main(args=None):
    args = docopt(__doc__, args)
    print(args)

    if args['flights']:
        solutions = core.scan(
            origs=args['<origins>'].split(','),
            dests=args['<destinations>'].split(','),
            earliest_to=date(2016, 11, 19),
            latest_to=date(2016, 11, 20),
            listener=cli_listener,
            max_flights=2,
        )

        render_solutions(solutions)
        return

    if args['airports']:
        airports = {data['name']: iata for iata, data in core.get_airports().items()}

        longest_key = max(map(len, airports))

        for airport in sorted(airports):
            print('%s: %s' % (airport.ljust(longest_key), airports[airport]))

        return


def render_solutions(solutions):
    for s in solutions:
        if len(s.flights) == 1:
            render_single_flight_solution(s)
            continue

        render_multiflight_solution(s)


def render_single_flight_solution(sol):
    print(format_flight(sol.flights[0]))


def format_flight(flight):
    return '{f.orig} > {f.dest} | {f.price}€ | {f.flight_number} | {date}'.format(
        f=flight,
        date=format_dates(flight.date_out, flight.date_in),
    )


def render_multiflight_solution(sol):
    print('{s.orig} > {s.dest} | {s.price}€ | {dates}'.format(s=sol, dates=format_dates(sol.date_out, sol.date_in)))

    for f in sol.flights:
        print('  - %s' % format_flight(f))


def format_dates(date_out, date_in):
    """
    :type date_out: datetime.datetime

    """
    full_format = '%a %d-%m-%Y %H:%M'
    only_time = '%H:%M'

    return '%s - %s' % (
        date_out.strftime(full_format),
        date_in.strftime(only_time if date_out.date() == date_in.date() else full_format),
    )

if __name__ == '__main__':
    main()
