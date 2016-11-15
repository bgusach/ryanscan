ryanscan
========

What is this?
-------------
A small tool to make easier the task of searching flights on Ryanair's website,
especially with multiple origins, destinations or possible connecting flights.

Why?
----
Because it is annoying to do it by hand, and it is a fun small project :).


How does it work?
-----------------
So far it only has a command line interface. For instance,
to find flights from Bremen to Valencia or Alicante within a given timeframe::

    $ ryanscan find BRE VLC 2016-12-20 2016-12-25
    ryanscan: Getting network
    ryanscan: Getting airports information
    ryanscan: 9 path(s) found
    ryanscan: Finding valid solutions
    BRE > VLC | Tue 2016-12-20 09:40 - 15:20 | 120.00€
      - BRE > STN | Tue 2016-12-20 09:40 - 10:10 | FR 3631 | 10.00€
      - STN > VLC | Tue 2016-12-20 11:50 - 15:20 | FR 1379 | 110.00€
    BRE > VLC | Thu 2016-12-22 07:00 - 15:05 | 260.00€
      - BRE > STN | Thu 2016-12-22 07:00 - 07:30 | FR 3631 | 10.00€
      - STN > VLC | Thu 2016-12-22 11:35 - 15:05 | FR 1379 | 250.00€

And there is a helper as well to find out the IATA codes of the airports::

    $ ryanscan airports find-airports bremen valencia london
    ryanscan: Finding airports
    Bremen (DE)           : BRE
    London (Gatwick) (GB) : LGW
    London (Luton) (GB)   : LTN
    London (Stansted) (GB): STN
    Valencia (ES)         : VLC


Type ``ryanscan --help`` for more.


TODO
----
- Add support for both ways search
- Accept minimum and maximum time between flights as a parameter