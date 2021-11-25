from wunderkafka.hotfixes.watchdog import parse_kinit

USER = 'my.user'
REALM = 'MYDOMAIN.COM'


def test_relative_regular():
    keytab = '{0}.keytab'.format(USER)
    kinit_cmd = 'kinit {0}@{1} -k -t {2}'.format(USER, REALM, keytab)
    assert parse_kinit(kinit_cmd) == (USER, REALM, keytab)


def test_absolute_with_domain():
    keytab = '/home/{0}@{1}/{0}.keytab'.format(USER, REALM.lower())
    kinit_cmd = 'kinit {0}@{1} -k -t {2}'.format(USER, REALM, keytab)
    assert parse_kinit(kinit_cmd) == (USER, REALM, keytab)
