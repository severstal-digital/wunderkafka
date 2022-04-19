# -*- coding: utf-8 -*-

import datetime

import pytest

from wunderkafka.hotfixes.watchdog.krb.ticket import clean_stdout, get_datetime

STDOUT1 = """
Ticket cache: FILE:/tmp/krb5cc_1000
Default principal: my.user@MYDOMAIN.COM

Valid starting       Expires              Service principal
05/19/2021 11:39:14  05/20/2021 11:39:14  krbtgt/MYDOMAIN.COM@MYDOMAIN.COM
        renew until 05/26/2021 11:39:14
"""

STDOUT2 = """
klist: No credentials cache found (filename: /tmp/krb5cc_1000)
"""

STDOUT3 = """
Ticket cache: FILE:/tmp/krb5cc_1000
Default principal: service.user@MYDOMAIN.COM

Valid starting     Expires            Service principal
05/18/21 21:02:14  05/19/21 21:02:14  krbtgt/MYDOMAIN.COM@MYDOMAIN.COM
        renew until 05/25/21 21:02:14
05/18/21 21:02:14  05/19/21 07:02:14  kafka/kafka-broker-01.MYDOMAIN.COM@MYDOMAIN.COM
        renew until 05/25/21 21:02:14
05/18/21 21:02:14  05/19/21 07:02:14  HTTP/kafka-broker-01.MYDOMAIN.COM@MYDOMAIN.COM
        renew until 05/25/21 21:02:14
"""


def test_parse_dates():
    unparsable = ('None', 'Expires')
    for st in unparsable:
        assert get_datetime(st) is None

    parsable = {
        '09.04.2021 21:45:41': 4,
        '04/15/2021 20:21:58': 15,
        '15.05.2021 11:22:12': 15,
        '04/09/2021 21:45:41': 9,
        '07/02/21 17:44:03': 2,
    }
    for st, day in parsable.items():
        dt = get_datetime(st)
        assert isinstance(dt, datetime.datetime)
        assert dt.year == 2021
        assert dt.day == day


user = 'my.user'
service_user = 'service.user'
REALM = 'MYDOMAIN.COM'


def test_check_stdout_user():
    res = clean_stdout(STDOUT1, user, REALM)
    assert len(res) == 1

    with pytest.raises(ValueError):
        clean_stdout(STDOUT1, service_user, REALM)

    # FixMe (tribunsky.kir): accidentally, BUG
    # with pytest.raises(ValueError):
    #     clean_stdout(STDOUT1, service_user, 'MYDOMAIN.COM@MYDOMAIN.COM')


def test_no_tickets():
    with pytest.raises(ValueError):
        clean_stdout(STDOUT2, service_user, REALM)

    with pytest.raises(ValueError):
        clean_stdout(STDOUT2, user, REALM)


def test_service_user():
    res = clean_stdout(STDOUT3, service_user, REALM)
    assert len(res) == 2

    with pytest.raises(ValueError):
        clean_stdout(STDOUT3, user, REALM)
