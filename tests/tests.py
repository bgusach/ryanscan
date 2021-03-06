# coding: utf-8

from __future__ import unicode_literals, absolute_import, division, print_function

from datetime import datetime as dt
from datetime import timedelta as delta
from unittest import TestCase

from ryanscan import core
from ryanscan.core import DateConstraint
from ryanscan.core import Solution
from ryanscan.core import BackendRequest
from ryanscan.core import Flight as F
from ryanscan.core import Edge as E


class Tests(TestCase):

    stations_data = {
        "airports": [
            {
                "routes": [
                    "region:xxxx",
                    "airport:AAA",
                    "airport:BBB",
                    "country:xxxx",
                    "country:xxxx",
                    "airport:DDD",
                    "city:xxxx",
                    "region:xxxx",
                    "city:xxxx",
                    "city:xxxx",
                    "region:xxxx"
                ],
                "iataCode": "CCC",
                "name": "Atlantis",
            },
            {
                "routes": [
                    "airport:FFF",
                    "airport:GGG",
                    "city:xxxx",
                    "region:xxxx",
                    "country:xxxx",
                    "airport:HHH",
                    "airport:III",
                    "airport:JJJ",
                    "airport:KKK",
                    "city:xxxx",
                    "airport:LLL",
                    "airport:MMM",
                    "airport:NNN",
                    "airport:OOO",
                    "airport:PPP",
                    "airport:AAA",
                ],
                "iataCode": "EEE",
                "name": "Villaconejos",
            }
        ]
    }

    def test_1(self):
        result = core.get_connections_from_stations_data(self.stations_data)

        expected = {
            'EEE': {
                'AAA',
                'FFF',
                'GGG',
                'HHH',
                'III',
                'JJJ',
                'KKK',
                'LLL',
                'MMM',
                'NNN',
                'OOO',
                'PPP',
            },

            'CCC': {
                'AAA',
                'BBB',
                'DDD',
            }

        }

        self.assertEqual(expected, result)

    def test_2(self):
        result = core.get_airport_names_from_raw_data(self.stations_data)
        expected = {
            'CCC': 'Atlantis',
            'EEE': 'Villaconejos',
        }

        self.assertEqual(result, expected)

    network = {
        'A': {'B', 'C', 'D'},
        'B': {'A', 'F'},
        'C': {'A', 'F', 'E'},
        'D': {'A', 'E'},
        'E': {'D', 'C', 'F'},
        'F': {'B', 'C', 'E'},
    }

    def test_3(self):
        """
        If enough depth is allowed, all the possible paths are discovered

        """
        res = set(map(tuple, core.find_paths(['A'], ['F'], self.network, max_flights=1000000)))
        expected = {
            (('A', 'B'), ('B', 'F')),
            (('A', 'C'), ('C', 'F')),
            (('A', 'C'), ('C', 'E'), ('E', 'F')),
            (('A', 'D'), ('D', 'E'), ('E', 'F')),
            (('A', 'D'), ('D', 'E'), ('E', 'C'), ('C', 'F')),
        }

        self.assertEqual(expected, res)

    def test_3b(self):
        expected = {
            (('A', 'B'), ('B', 'F')),
            (('A', 'C'), ('C', 'F')),
        }

        res = set(map(tuple, core.find_paths(['A'], ['F'], self.network, max_flights=2)))
        self.assertEqual(expected, res)

    def test_3c(self):
        """
        From multiple starts to multiple destinations

        """
        res = set(map(tuple, core.find_paths(['A', 'B'], ['F', 'E'], self.network, max_flights=1000000)))
        expected = {
            (('B', 'F'), ),
            (('A', 'C'), ('C', 'F')),
            (('A', 'C'), ('C', 'E')),
            (('A', 'D'), ('D', 'E')),
        }
        self.assertEqual(expected, res)

    def test_6(self):
        paths = [[E('A', 'B'), E('B', 'C')], [E('D', 'E')]]
        dates_to = core.DateInterval(dt(2016, 10, 10), dt(2016, 10, 20))
        result = core.calculate_needed_requests(paths, dates_to)

        self.assertEqual({
            BackendRequest('A', 'B', dt(2016, 10, 10), None),
            BackendRequest('A', 'B', dt(2016, 10, 17), None),
            BackendRequest('B', 'C', dt(2016, 10, 10), None),
            BackendRequest('B', 'C', dt(2016, 10, 17), None),
            BackendRequest('D', 'E', dt(2016, 10, 10), None),
            BackendRequest('D', 'E', dt(2016, 10, 17), None),
        }, result)

    def test_7(self):
        """
        When start and end date are the same, we still query once

        """
        paths = [[E('A', 'B'), E('B', 'C')], [E('D', 'E')]]
        dates_to = core.DateInterval(dt(2016, 10, 10), dt(2016, 10, 10))
        result = core.calculate_needed_requests(paths, dates_to)

        self.assertEqual({
            BackendRequest('A', 'B', dt(2016, 10, 10), None),
            BackendRequest('B', 'C', dt(2016, 10, 10), None),
            BackendRequest('D', 'E', dt(2016, 10, 10), None),
        }, result)

    def test_8(self):
        """
        Query calculator works fine over longer time periods

        """
        paths = [[E('A', 'B')]]
        dates_to = core.DateInterval(dt(2016, 10, 1), dt(2016, 11, 15))
        result = core.calculate_needed_requests(paths, dates_to)

        self.assertEqual({
            BackendRequest('A', 'B', dt(2016, 10, 1), None),
            BackendRequest('A', 'B', dt(2016, 10, 8), None),
            BackendRequest('A', 'B', dt(2016, 10, 15), None),
            BackendRequest('A', 'B', dt(2016, 10, 22), None),
            BackendRequest('A', 'B', dt(2016, 10, 29), None),
            BackendRequest('A', 'B', dt(2016, 11, 5), None),
            BackendRequest('A', 'B', dt(2016, 11, 12), None),
        }, result)

    def test_9(self):
        """
        are_flights_compatible: positive single flight

        """
        flights = [make_flight()]
        constraint = DateConstraint(
            earliest_out=dt(2016, 1, 1),
            latest_in=dt(2016, 1, 1, 23, 59, 59),
            latest_out=dt(2016, 1, 1, 23, 59, 59),
            min_between_flights=delta(hours=1),
            max_between_flights=delta(hours=5),
        )

        self.assertTrue(core.are_flights_compatible(flights, constraint))

    def test_10(self):
        """
        are_flights_compatible: negative single flight - arrives too late

        """
        flight = make_flight()

        constraint = DateConstraint(
            earliest_out=dt(2016, 1, 1),
            latest_out=dt(2016, 1, 1, 23, 59, 59),
            latest_in=flight.date_in - delta(hours=1),  # Failing constraint
            min_between_flights=delta(hours=1),
            max_between_flights=delta(hours=5),
        )

        self.assertFalse(core.are_flights_compatible([flight], constraint))

    def test_11(self):
        """
        are_flights_compatible: negative single flight - departs too late

        """
        flight = make_flight()

        constraint = DateConstraint(
            earliest_out=dt(2016, 1, 1),
            latest_out=flight.date_out - delta(hours=1),  # Failing condition
            latest_in=dt(2016, 1, 1, 23, 59, 59),
            min_between_flights=delta(hours=1),
            max_between_flights=delta(hours=5),
        )

        self.assertFalse(core.are_flights_compatible([flight], constraint))

    def test_12(self):
        """
        are_flights_compatible: negative single flight - departs too early

        """
        flight = make_flight()

        constraint = DateConstraint(
            earliest_out=flight.date_out + delta(hours=1),
            latest_out=dt(2016, 1, 1, 23, 59, 59),
            latest_in=dt(2016, 1, 1, 23, 59, 59),
            min_between_flights=delta(hours=1),
            max_between_flights=delta(hours=5),
        )

        self.assertFalse(core.are_flights_compatible([flight], constraint))

    def test_13(self):
        """
        are_flights_compatible: positive multiple flights

        """
        f1 = make_flight()
        f2 = make_flight(orig=f1.dest, dest='C', date_out=f1.date_in + delta(hours=1), date_in=f1.date_in + delta(hours=3))

        constraint = DateConstraint(
            earliest_out=dt(2016, 1, 1),
            latest_out=dt(2016, 1, 1, 23, 59, 59),
            latest_in=dt(2016, 1, 1, 23, 59, 59),
            min_between_flights=delta(hours=1),
            max_between_flights=delta(hours=5),
        )

        self.assertTrue(core.are_flights_compatible([f1, f2], constraint))

    def test_14(self):
        """
        Negative are_flights_compatible: there is not enough time between flights

        """
        f1 = make_flight()
        f2 = make_flight(orig=f1.dest, dest='C', date_out=f1.date_in, date_in=f1.date_in + delta(hours=3))

        constraint = DateConstraint(
            earliest_out=dt(2016, 1, 1),
            latest_out=dt(2016, 1, 1, 23, 59, 59),
            latest_in=dt(2016, 1, 1, 23, 59, 59),
            min_between_flights=delta(hours=1),
            max_between_flights=delta(hours=5),
        )

        self.assertFalse(core.are_flights_compatible([f1, f2], constraint))

    def test_15(self):
        """
        Negative are_flights_compatible: there is too much time between flights

        """
        f1 = make_flight()
        f2 = make_flight(orig=f1.dest, dest='C', date_out=f1.date_in + delta(hours=10), date_in=f1.date_in + delta(hours=13))

        constraint = DateConstraint(
            earliest_out=dt(2016, 1, 1),
            latest_out=dt(2016, 1, 1, 23, 59, 59),
            latest_in=dt(2016, 1, 1, 23, 59, 59),
            min_between_flights=delta(hours=1),
            max_between_flights=delta(hours=5),
        )

        self.assertFalse(core.are_flights_compatible([f1, f2], constraint))

    def test_16(self):
        """
        get_path_solutions: generated solutions contain the right flights

        """
        path = [E('A', 'B'), E('B', 'C'), E('C', 'D')]

        f0, f1, f2, f3, f4, f5 = [make_flight() for _ in range(6)]

        edge2flights = {
            E('A', 'B'): [f0, f1],
            E('B', 'C'): [f2, f3],
            E('C', 'D'): [f4, f5],
        }

        solutions = core.get_path_solutions(
            path=path,
            edge2flights=edge2flights,

            # Just mock the compatibility test
            date_constraint=None,
            are_flights_compatible=return_true,
        )

        # In this test we don't care too much about anything but the generated routes
        calculated_flights = [s.flights for s in solutions]
        expected = [
            [f0, f2, f4],
            [f0, f2, f5],
            [f0, f3, f4],
            [f0, f3, f5],
            [f1, f2, f4],
            [f1, f2, f5],
            [f1, f3, f4],
            [f1, f3, f5],
        ]

        self.assertEqual(calculated_flights, expected)

    def test_17(self):
        """
        get_path_solutions: generated solutions contain the right values from its flights

        """
        path = [E('A', 'B'), E('B', 'C')]

        f0 = make_flight('A', 'B')
        f1 = make_flight('B', 'C', date_in=f0.date_in + delta(hours=5), price=66)
        f2 = make_flight('B', 'C', date_in=f0.date_in + delta(hours=10), price=101)

        edge2flights = {
            E('A', 'B'): [f0],
            E('B', 'C'): [f1, f2],
        }

        result = core.get_path_solutions(
            path=path,
            edge2flights=edge2flights,

            # Just mock the compatibility test
            date_constraint=None,
            are_flights_compatible=return_true,
        )

        expected = [
            Solution(orig='A', dest='C', date_out=f0.date_out, date_in=f1.date_in, flights=[f0, f1], price=f0.price + f1.price),
            Solution(orig='A', dest='C', date_out=f0.date_out, date_in=f2.date_in, flights=[f0, f2], price=f0.price + f2.price),
        ]

        self.assertEqual(result, expected)


def return_true(*args, **kwargs):
    return True


def make_flight(orig='A', dest='B', date_out=dt(2016, 1, 1, 10, 30), date_in=dt(2016, 1, 1, 13, 30), price=100, flight_number='abc'):
    return F(**locals())
