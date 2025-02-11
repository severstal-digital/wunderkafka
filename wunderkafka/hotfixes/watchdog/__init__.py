import os
import time
import subprocess
from typing import Any, Set, Dict, Tuple, Optional
from dataclasses import dataclass

from confluent_kafka import libversion

from wunderkafka.logger import logger
from wunderkafka.config.rdkafka import RDKafkaConfig
from wunderkafka.config.generated import enums
from wunderkafka.hotfixes.watchdog.types import Watchdog

REQUIRES_KERBEROS = frozenset([enums.SecurityProtocol.sasl_ssl, enums.SecurityProtocol.sasl_plaintext])


class NonRepetitiveLogger:

    def __init__(self) -> None:
        self._logged: set[int] = set()

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
class KinitParams:
    user: str
    realm: str
    keytab: str
    cmd: str

    @property
    def keytab_filename(self) -> str:
        return self.keytab.split(os.path.sep)[-1]

    @property
    def principal(self) -> str:
        return f'{self.user}@{self.realm}'


def get_version() -> tuple[int, ...]:
    semver, _ = libversion()
    return split(semver)


def split(version: str) -> tuple[int, ...]:
    return tuple(int(digit) for digit in version.split('.')[:2])


class Borg:
    _shared_state: dict[str, Any] = {}

    def __init__(self) -> None:
        self.__dict__ = self._shared_state


def parse_kinit(kinit_cmd: str) -> KinitParams:
    kinit_cmd_msg = f'kinit_cmd: `{kinit_cmd}`'
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
        raise ValueError(f"Couldn't get keytab: {keytab} ({kinit_cmd_msg})")
    if len(parts) != 1:
        raise ValueError(f"Couldn't parse {kinit_cmd_msg}")
    [principal] = parts
    delim = '@'
    user, realm = principal.split(delim)
    if not (user and realm):
        raise ValueError(f"Couldn't parse principal: {principal} ({kinit_cmd_msg})")
    return KinitParams(user=user, realm=realm, keytab=keytab, cmd=kinit_cmd)



def init_kerberos(params: KinitParams, timeout: int = 60) -> None:
    t0 = time.perf_counter()
    refresh_cmd = params.cmd.split()
    logger.info(f'Refreshing krb-ticket ({params.principal}|{params.keytab_filename})...')
    try:
        subprocess.run(refresh_cmd, timeout=timeout, stdout=subprocess.PIPE, check=True)
    # Will retry shortly
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        logger.error(exc.output)
        logger.error(exc.stdout)
        logger.error(exc.stderr)
        logger.error(f'Command: {refresh_cmd} exit error: {str(exc)}')
        logger.warning("Krb not refreshed!")
    else:
        duration = int(1000 * (time.perf_counter() - t0))
        logger.info(f'Refreshed! ({duration} ms)')

