# coding: utf-8

from __future__ import unicode_literals, absolute_import, division, print_function

from datetime import datetime
from unittest import TestCase

import core
from core import DateInterval
from core import BackendRequest


class Tests(TestCase):

    data = {
        "airports": [
            {
                "routes": [
                    "region:SICILY",
                    "airport:STN",
                    "airport:CAG",
                    "country:it",
                    "country:gb",
                    "airport:TPS",
                    "city:TRAPANI",
                    "region:SARDINIA",
                    "city:CAGLIARI",
                    "city:LONDON",
                    "region:GREATER_LONDON"
                ],
                "iataCode": "PMF",
                "categories": [
                    "FAM",
                    "SPR",
                    "FST",
                    "CTY",
                    "CUL",
                    "OUT"
                ],
                "name": "Parma",
                "cityCode": "PARMA",
                "countryCode": "it",
                "seoName": "parma",
                "regionCode": "EMILIA-ROMAGNA",
                "coordinates": {
                    "latitude": 44.8245,
                    "longitude": 10.2964
                },
                "priority": 115,
                "seasonalRoutes": [],
                "currencyCode": "EUR",
                "base": False
            },
            {
                "routes": [
                    "airport:VLC",
                    "airport:LPA",
                    "city:TENERIFE",
                    "region:CANARY_ISLES",
                    "country:gr",
                    "airport:WMI",
                    "airport:BGY",
                    "airport:FCO",
                    "airport:MAD",
                    "city:GRAN_CANARIA",
                    "airport:PMI",
                    "airport:AGP",
                    "airport:SOF",
                    "city:MILAN",
                    "city:WARSAW",
                    "city:BERLIN",
                    "region:COSTA_DE_SOL",
                    "city:BARCELONA",
                    "city:SOFIA",
                    "country:dk",
                    "country:pt",
                    "city:ROME",
                    "country:lv",
                    "region:COSTA_BRAVA",
                    "country:pl",
                    "city:VALENCIA",
                    "airport:DUB",
                    "airport:CFU",
                    "country:de",
                    "airport:STN",
                    "airport:OPO",
                    "city:CORFU",
                    "city:PORTO",
                    "country:es",
                    "city:BENIDORM",
                    "airport:SXF",
                    "airport:RIX",
                    "airport:MLA",
                    "country:mt",
                    "city:PALMA",
                    "airport:CPH",
                    "city:MALAGA",
                    "country:it",
                    "region:IONIAN_ISLANDS_GREEK_ISLANDS",
                    "airport:ALC",
                    "country:ie",
                    "airport:FAO",
                    "city:ALGARVE",
                    "city:LONDON",
                    "airport:BCN",
                    "country:gb",
                    "airport:TFS",
                    "city:DUBLIN",
                    "city:MADRID",
                    "city:MALTA",
                    "airport:CIA",
                    "country:bg",
                    "city:COPENHAGEN",
                    "city:RIGA",
                    "region:COSTA_BLANCA",
                    "region:GREATER_LONDON"
                ],
                "iataCode": "CGN",
                "categories": [
                    "FAM",
                    "SPR",
                    "FST",
                    "CTY",
                    "CUL",
                    "OUT",
                    "XMS"
                ],
                "name": "Cologne",
                "cityCode": "COLOGNE",
                "countryCode": "de",
                "seoName": "cologne-bonn",
                "regionCode": "NORTH_RHINE-WESTPHALIA",
                "coordinates": {
                    "latitude": 50.8659,
                    "longitude": 7.14274
                },
                "priority": 80,
                "seasonalRoutes": [],
                "currencyCode": "EUR",
                "base": True
            }
        ]
    }

    def test_1(self):
        result = core.get_connections_from_stations_data(self.data)

        expected = {
            'CGN': {
                'VLC',
                'LPA',
                'WMI',
                'BGY',
                'FCO',
                'MAD',
                'PMI',
                'AGP',
                'SOF',
                'DUB',
                'CFU',
                'STN',
                'OPO',
                'SXF',
                'RIX',
                'MLA',
                'CPH',
                'ALC',
                'FAO',
                'BCN',
                'TFS',
                'CIA',
            },

            'PMF': {
                'STN',
                'CAG',
                'TPS',
            }

        }

        self.assertEqual(expected, result)

    def test_2(self):
        result = core.get_airport_names_from_raw_data(self.data)
        expected = {
            'PMF': 'Parma',
            'CGN': 'Cologne',
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
        expected = {
            ('A', 'B', 'F'),
            ('A', 'C', 'F'),
            ('A', 'C', 'E', 'F'),
            ('A', 'D', 'E', 'F'),
            ('A', 'D', 'E', 'C', 'F'),
        }

        res = set(map(tuple, core.find_paths({'A'}, {'F'}, self.network, max_flights=1000000)))
        self.assertEqual(expected, res)

    def test_4(self):
        expected = {
            ('A', 'B', 'F'),
            ('A', 'C', 'F'),
        }

        res = set(map(tuple, core.find_paths({'A'}, {'F'}, self.network, max_flights=2)))
        self.assertEqual(expected, res)

    def test_5(self):
        expected = [(1, 2), (2, 3), (3, 4)]
        res = core.get_segments_from_path([1, 2, 3, 4])

        self.assertEqual(expected, res)

    def test_6(self):
        paths = [['A', 'B', 'C'], ['D', 'E']]
        dates_to = core.DateInterval(datetime(2016, 10, 10), datetime(2016, 10, 20))
        result = core.calculate_needed_requests(paths, dates_to)

        self.assertEqual({
            BackendRequest('A', 'B', datetime(2016, 10, 10), None),
            BackendRequest('A', 'B', datetime(2016, 10, 17), None),
            BackendRequest('B', 'C', datetime(2016, 10, 10), None),
            BackendRequest('B', 'C', datetime(2016, 10, 17), None),
            BackendRequest('D', 'E', datetime(2016, 10, 10), None),
            BackendRequest('D', 'E', datetime(2016, 10, 17), None),
        }, result)

    def test_7(self):
        """
        When start and end date are the same, we still query once

        """
        paths = [['A', 'B', 'C'], ['D', 'E']]
        dates_to = core.DateInterval(datetime(2016, 10, 10), datetime(2016, 10, 10))
        result = core.calculate_needed_requests(paths, dates_to)

        self.assertEqual({
            BackendRequest('A', 'B', datetime(2016, 10, 10), None),
            BackendRequest('B', 'C', datetime(2016, 10, 10), None),
            BackendRequest('D', 'E', datetime(2016, 10, 10), None),
        }, result)
