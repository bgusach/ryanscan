ryanscan
========

What is this?
-------------
A small tool to make easier the task of searching flights on Ryanair's website,
especially with multiple origins, destinations or possible connecting flights.


Why?
----
Because it is annoying to do it by hand, and it is a fun small project :).


Requirements
------------
Should work with Python 2.7 and any Python 3 version. However this has not been thoroughly
tested. If you find and issue, do not hesitate to open an issue on github.

You will need pip to install it. Virtualenv is recommended but not necessary.


How to install
--------------
Since this is not in PyPI, you need to clone the repository::

    git clone https://github.com/bgusach/ryanscan.git

Optionally create a virtualenv and activate it. Activating it depends on your shell. If you
are using bash the following lines should work::

    virtualenv env
    . env/bin/activate


Finally install ``ryanscan``::

    pip install .



How does it work?
-----------------
**IMPORTANT**: By using this programme you agree to the `Terms of Use of the Ryanair website
<https://www.ryanair.com/gb/en/corporate/terms-of-use>`_

So far it only has a command line interface. First of all, you need to know the IATA
codes of the airports you want to query. The easiest way is to use the ``find-airports``
command like this::

    $ ryanscan find-airports bremen valencia alicante
    ryanscan: Finding airports
    Alicante (ES): ALC
    Bremen (DE)  : BRE
    Valencia (ES): VLC


Once you have the IATA codes, you can use the ``find-flights`` command. Let's say we want
to query what flights are available from Bremen to Valencia or Alicante within a given timeframe
(disclaimer: this is not real data)::

    $ ryanscan find-flights BRE VLC,ALC 2016-10-20 2016-10-25
    ryanscan: Getting network
    ryanscan: Getting airports information
    ryanscan: 16 path(s) found
    ryanscan: Finding valid solutions
    BRE > VLC | Thu 2016-10-20 09:40 - 15:20 | 120.00€
      - BRE > STN | Thu 2016-10-20 09:40 - 10:10 | FR 3631 | 10.00€
      - STN > VLC | Thu 2016-10-20 11:50 - 15:20 | FR 1379 | 110.00€
    BRE > VLC | Sat 2016-10-22 07:00 - 15:05 | 260.00€
      - BRE > STN | Sat 2016-10-22 07:00 - 07:30 | FR 3631 | 10.00€
      - STN > VLC | Sat 2016-10-22 11:35 - 15:05 | FR 1379 | 250.00€
    BRE > ALC | Sun 2016-10-23 15:50 - 18:45 | FR 9057 | 250.00€


Type ``ryanscan --help`` to see further options.


TODO
----
- Add support for both ways search
- Accept minimum and maximum time between flights as a parameter