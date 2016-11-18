# coding: utf-8

from __future__ import unicode_literals, absolute_import, division

import requests
from .tools import log_info


class BackendError(Exception):
    
    def __init__(self, msg, details):
        self.msg = msg
        self.details = details


def get_airports_raw_data():
    log_info('Getting airports information')
    return get_json('https://api.ryanair.com/aggregate/3/common?embedded=airports&market=en-ie')


def get_json(path, **kwargs):
    err_msg = 'Impossible to communicate with Ryanair backend'

    try:
        r = requests.get(path, **kwargs)

    except Exception:
        raise BackendError(err_msg, traceback.format_exc())

    if not r.ok:
        raise BackendError(err_msg, 'Backend responded with status code %s' % r.status_code)

    return r.json()



def execute_request(request):
    query = {
        'ADT': 1,
        'CHD': 0,
        'DateOut': request.date_to.isoformat(),
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


def get_airports():
    log_info('Finding airports')
    return get_json('https://desktopapps.ryanair.com/en-ie/res/stations')

