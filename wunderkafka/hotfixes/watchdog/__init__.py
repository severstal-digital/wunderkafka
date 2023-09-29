import os
import time
import subprocess
from typing import Any, Set, Dict, Tuple, Optional, List
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


class NonRepetitiveLogger(object):

    def __init__(self) -> None:
        self._logged: Set[int] = set()

    def _log(self, message: str, *, info: bool = True) -> None:
        hashed = hash(message)
        if hashed in self._logged:
            return
        if info:
            logger.info(message)
        else:
            logger.warning(message)
        self._logged.add(hashed)

    def info(self, message: str) -> None:
        self._log(message)

    def warning(self, message: str) -> None:
        self._log(message, info=False)


log_once = NonRepetitiveLogger()


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
        log_once.info('Watchdog: please check if there are any issues with SASL GSSAPI in the upstream.')
        return config, watchdog

    if version == (1, 7):
        msg = 'rewriting config. For more info, please, check https://github.com/edenhill/librdkafka/issues/3430'
        log_once.warning('Watchdog: {0}'.format(msg))
        config.sasl_kerberos_min_time_before_relogin = 86400000
    elif version < (1, 7):
        msg = ' '.join([
            'adding watchdog thread.',
            'Prior to 1.7.0 kinit refresh via librdkafka may cause blocking.',
            'For more info, please, check https://github.com/edenhill/librdkafka/pull/3340',
        ])
        log_once.warning('Watchdog: {0}'.format(msg))
        params = parse_kinit(config.sasl_kerberos_kinit_cmd)
        config.sasl_kerberos_min_time_before_relogin = 0
        watchdog = KrbWatchDog()
        watchdog.add(params)
    return config, watchdog


class Borg(object):
    _shared_state: Dict[str, Any] = {}

    def __init__(self) -> None:
        self.__dict__ = self._shared_state


def parse_kinit(kinit_cmd: str) -> KinitParams:
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
    if keytab is None:
        raise ValueError("Couldn't get keytab: {0} ({1})".format(keytab, kinit_cmd_msg))
    if len(parts) != 1:
        raise ValueError("Couldn't parse {0}".format(kinit_cmd_msg))
    [principal] = parts
    delim = '@'
    user, realm = principal.split(delim)
    if not (user and realm):
        raise ValueError("Couldn't parse principal: {0} ({1})".format(principal, kinit_cmd_msg))
    return KinitParams(user=user, realm=realm, keytab=keytab, cmd=kinit_cmd)


class KerberosRefreshThread(Thread):
    def __init__(self, params: Set[KinitParams]) -> None:
        super().__init__(daemon=True)

        self._params_refresh: Dict[KinitParams, float] = {}
        for p in params:
            self._refresh_krb(p)

        logger.info("Kerberos thread: initiated")

    def run(self) -> None:
        logger.info("Kerberos thread: started")
        while True:
            for param in self._params_refresh:
                if time.time() >= self._params_refresh[param]:
                    self._refresh_krb(param)
            time.sleep(0.01)

    def update_keytabs(self, params: Set[KinitParams]) -> None:
        for param in params:
            if param not in self._params_refresh:
                self._refresh_krb(param)
                logger.debug("The addition of the new keytab ({0}|{1}) was successful".format(
                    param.principal, param.keytab_filename
                ))

    def _refresh_krb(self, params: KinitParams) -> None:
        t0 = time.perf_counter()
        refresh_cmd = params.cmd.split()
        logger.info('Refreshing krb-ticket ({0}|{1})...'.format(params.principal, params.keytab_filename))
        try:
            subprocess.run(refresh_cmd, stdout=subprocess.PIPE, check=True)
        # Will retry  shortly
        except subprocess.CalledProcessError as exc:
            logger.error(exc.output)
            logger.error(exc.stdout)
            logger.error(exc.stderr)
            logger.error('Command: {0} exit code: {1}'.format(refresh_cmd, exc.returncode))
        else:
            duration = int(1000 * (time.perf_counter() - t0))
            logger.info('Refreshed! ({0} ms)'.format(duration))
            self._params_refresh[params] = get_expiration_ts(params.user, params.realm)
            logger.debug('Nearest existing: {0} keytab: ({1}|{2})'.format(
                ts2dt(self._params_refresh[params]), params.principal, params.keytab_filename)
            )


class KrbWatchDog(Borg):
    __thread: Optional[KerberosRefreshThread] = None
    __kinit_params: Set[KinitParams] = set()

    def __init__(self) -> None:
        super().__init__()
        self._ensure_started()

    def add(self, params: KinitParams) -> None:
        if params not in self.__kinit_params:
            self.__kinit_params.add(params)
            self._ensure_started()

    @property
    def count_params(self) -> int:
        return len(self.__kinit_params)

    def _ensure_started(self) -> None:
        if self.__thread is None:
            self.__thread = KerberosRefreshThread(self.__kinit_params)
            self.__thread.start()
        else:
            self.__thread.update_keytabs(self.__kinit_params)
        if self.__thread.is_alive() is False:
            self.__thread = KerberosRefreshThread(self.__kinit_params)
            self.__thread.start()

    def __call__(self) -> None:
        self._ensure_started()
