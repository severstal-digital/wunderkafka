from unittest.mock import Mock

from pytest import MonkeyPatch

from wunderkafka.hotfixes.watchdog import KrbWatchDog, KinitParams


def test_krb_watchdog(monkeypatch: MonkeyPatch) -> None:
    params = [KinitParams(user=f'user_{i}', realm='realm', keytab=f'keytab{i}', cmd='cmd') for i in range(10)]
    monkeypatch.setattr('wunderkafka.hotfixes.watchdog.KrbWatchDog._ensure_started', Mock())
    for i, p in enumerate(params, start=1):
        thread = KrbWatchDog()
        thread.add(p)
        assert thread.count_params == i
