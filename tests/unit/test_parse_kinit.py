import pytest

from wunderkafka.hotfixes.watchdog import parse_kinit, KinitParams

USER = 'my.user'
REALM = 'MYDOMAIN.COM'


@pytest.mark.parametrize(
    'keytab',
    ['{0}.keytab'.format(USER), '/home/{0}@{1}/{0}.keytab'.format(USER, REALM.lower())]
)
def test_parse_kinit(keytab: str) -> None:
    kinit_cmd = 'kinit {0}@{1} -k -t {2}'.format(USER, REALM, keytab)
    assert parse_kinit(kinit_cmd) == KinitParams(user=USER, realm=REALM, keytab=keytab, cmd=kinit_cmd)
