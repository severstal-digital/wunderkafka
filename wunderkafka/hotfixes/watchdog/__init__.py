import os
import time
import subprocess
from typing import Any, Dict, Tuple, Optional
from threading import Thread
from dataclasses import dataclass

from confluent_kafka import libversion

from wunderkafka.time import ts2dt
from wunderkafka.logger import logger
from wunderkafka.config.rdkafka import RDKafkaConfig
from wunderkafka.config.generated import enums
from wunderkafka.hotfixes.watchdog.types import Watchdog
from wunderkafka.hotfixes.watchdog.krb.ticket import get_expiration_ts

REQUIRES_KERBEROS = frozenset([enums.SecurityProtocol.sasl_ssl, enums.SecurityProtocol.sasl_plaintext])


@dataclass(frozen=True)
class KinitParams(object):
    user: str
    realm: str
    keytab: str
    cmd: str

    @property
    def keytab_filename(self) -> str:
        return self.keytab.split(os.path.sep)[-1]

    @property
    def principal(self) -> str:
        return '{0}@{1}'.format(self.user, self.realm)


def get_version() -> Tuple[int, ...]:
    semver, _ = libversion()
    return split(semver)


def split(version: str) -> Tuple[int, ...]:
    return tuple(int(digit) for digit in version.split('.')[:2])


# ToDo (tribunsky.kir): Currently will log for every created producer/consumer. Move messaging to Watchdog itself.
def check_watchdog(
    config: RDKafkaConfig,
    version: Tuple[int, ...] = get_version(),
) -> Tuple[RDKafkaConfig, Optional[Watchdog]]:
    watchdog = None
    if config.security_protocol.value not in REQUIRES_KERBEROS:
        return config, watchdog
    if version > (1, 7):
        logger.info('Watchdog: please check if there are any issues with SASL GSSAPI in the upstream.')
        return config, watchdog

    if version == (1, 7):
        msg = 'rewriting config. For more info, please, check https://github.com/edenhill/librdkafka/issues/3430'
        logger.warning('Watchdog: {0}'.format(msg))
        config.sasl_kerberos_min_time_before_relogin = 86400000
    elif version < (1, 7):
        msg = ' '.join([
            'adding watchdog thread.',
            'Prior to 1.7.0 kinit refresh via librdkafka may cause blocking.',
            'For more info, please, check https://github.com/edenhill/librdkafka/pull/3340',
        ])
        logger.warning('Watchdog: {0}'.format(msg))
        user, realm, keytab = parse_kinit(config.sasl_kerberos_kinit_cmd)
        config.sasl_kerberos_min_time_before_relogin = 0
        watchdog = KrbWatchDog(KinitParams(
            user=user,
            realm=realm,
            keytab=keytab,
            cmd=config.sasl_kerberos_kinit_cmd,
        ))
    return config, watchdog


class Borg(object):
    _shared_state: Dict[str, Any] = {}

    def __init__(self) -> None:
        self.__dict__ = self._shared_state


def parse_kinit(kinit_cmd: str) -> Tuple[str, str, str]:
    kinit_cmd_msg = 'kinit_cmd: `{0}`'.format(kinit_cmd)
    parts = []
    keytab = None
    prev = None
    for word in kinit_cmd.split():
        normalized = word.strip()
        if prev == '-t':
            keytab = normalized
        elif len(normalized) > 2 and normalized != 'kinit':
            parts.append(normalized)
        prev = normalized

    if len(parts) != 1:
        raise ValueError("Couldn't parse {0}".format(kinit_cmd_msg))
    [principal] = parts
    delim = '@'
    user, realm = principal.split(delim)
    if not (user and realm):
        raise ValueError("Couldn't parse principal: {0} ({1})".format(principal, kinit_cmd_msg))
    return user, realm, keytab


# ToDo (tribunsky.kir): BUG. Currently handling only single kinit_cmd while it is possible to create more than one
#                            consumer with different keytabs
class KerberosRefreshThread(Thread):
    def __init__(self, params: KinitParams) -> None:
        super().__init__()
        self.daemon = True

        self._params = params
        self._refresh_cmd = params.cmd.split()

        self._refreshed = 0
        self._next_refresh_ts = 0.0

        self.refresh()
        logger.info("Kerberos thread is started")

    def run(self) -> None:
        while True:
            if time.time() >= self._next_refresh_ts:
                self.refresh()
            time.sleep(0.01)

    def refresh(self) -> None:
        t0 = time.perf_counter()

        logger.info('Refreshing krb-ticket ({0}|{1})...'.format(self._params.principal, self._params.keytab_filename))
        try:
            subprocess.run(self._refresh_cmd, stdout=subprocess.PIPE, check=True)
        # Will retry  shortly
        except subprocess.CalledProcessError as exc:
            logger.error(exc.output)
            logger.error(exc.stdout)
            logger.error(exc.stderr)
        else:
            duration = int(1000 * (time.perf_counter() - t0))
            logger.info('Refreshed! ({0} ms)'.format(duration))
            self._next_refresh_ts = get_expiration_ts(self._params.user, self._params.realm)
            logger.debug('Nearest update: {0}'.format(ts2dt(self._next_refresh_ts)))


class KrbWatchDog(Borg):
    __thread: Optional[KerberosRefreshThread] = None

    def __init__(self, params: KinitParams):
        super().__init__()
        self.__kinit_params: KinitParams = params
        self._ensure_started()

    def _ensure_started(self) -> None:
        if self.__thread is None:
            self.__thread = KerberosRefreshThread(self.__kinit_params)
            self.__thread.start()
        if self.__thread.is_alive() is False:
            self.__thread = KerberosRefreshThread(self.__kinit_params)
            self.__thread.start()

    def __call__(self) -> None:
        self._ensure_started()
