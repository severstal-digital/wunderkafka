import os
import time
import datetime
import subprocess
from typing import Optional

try:
    from dateutil import parser
except ImportError:
    HAS_DATEUTIL = False
else:
    HAS_DATEUTIL = True

from wunderkafka.logger import logger

# ToDo (tribunsky.kir): move it to platform as it is linux implementation


def check_posix() -> None:
    """
    Check if POSIX locale available.

    Why subprocessing:
    Python's `locale` and linux's `locale -a` behaves differently.

    Example:

    .. code-block:: console

        root@f1cde05f6fdd:/# locale -a
        C
        C.UTF-8
        POSIX
        root@f1cde05f6fdd:/# python
        Python 3.9.7 (default, Sep  3 2021, 20:10:26)
        [GCC 10.2.1 20210110] on linux
        Type "help", "copyright", "credits" or "license" for more information.
        >>> import locale
        >>> len(locale.locale_alias.items())
        588

    :returns:
    """
    try:
        proc = subprocess.run(['locale', '-a'], stdout=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as exc:
        logger.error(exc.output)
        logger.error(exc.stdout)
        logger.error(exc.stderr)
        logger.error(f'locale exit code: {exc.returncode}')
    else:
        lines = {line.strip() for line in proc.stdout.split(b'\n')}
        if b'POSIX' in lines:
            logger.debug('POSIX locale found.')
            return
        if b'posix' in {line.lower() for line in lines}:
            logger.warning(f'Found POSIX, but in lower-case. Please, check `locale -a` ({lines})')
            return
        logger.warning("Couldn't find any POSIX in locales. May misbehave.")


def clean_stdout(stdout: str, krb_user: str = '', krb_realm: str = '') -> set[str]:
    date_lines = set()
    for line in stdout.split('\n'):
        if krb_realm in line and krb_user not in line:
            _, _, dt, tm, *_ = line.split()
            date_lines.add(f'{dt} {tm}')

    if not date_lines:
        raise ValueError(f'Found no expiration dates. Please, check stdout:\n{stdout}')
    logger.debug(f'Got {len(date_lines)} expiration dates')
    return date_lines


def get_expiration_ts(krb_user: str, krb_realm: str, default_timeout: float = 60.0) -> float:
    """
    Get nearest ts when to refresh kerberos ticket, if we can.

    If we can't (no klist, no dates parsed), default timeout to refresh is 60.0 seconds is like in librdkafka.

    If we parsed some invalid data in the past, current timestamp is provided to refresh immediately.
    """
    klist_cmd = ['klist']
    # Using default env, BUT with overridden locale:
    # POSIX locale shall exist in any environment and klist changes it's output
    new_env = {**os.environ, 'LC_ALL': 'POSIX'}
    # logger.debug('Subprocess env to run klist: {0}'.format(new_env))
    try:
        proc = subprocess.run(klist_cmd, timeout=default_timeout, stdout=subprocess.PIPE, check=True, env=new_env)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        logger.error(exc.output)
        logger.error(exc.stdout)
        logger.error(exc.stderr)
        logger.error(f'klist exit: {str(exc)}')
        return time.time() + default_timeout
    else:
        expire_dates = []
        for dt_str in clean_stdout(proc.stdout.decode(), krb_user, krb_realm):
            dt = get_datetime(dt_str)
            if dt is not None:
                expire_dates.append(dt)
        logger.debug(f'Parsed dates: {expire_dates}')
        if not expire_dates:
            logger.warning('Got not expiration dates')
            return time.time() + default_timeout
        # expire_dates.append(datetime.datetime.now() + datetime.timedelta(seconds=default_timeout))
        delta = min(expire_dates) - datetime.datetime.now()
        timeout = delta.total_seconds()
        if timeout <= 1:
            return time.time()
        return time.time() + timeout/2.0


def get_datetime(string: str) -> Optional[datetime.datetime]:
    if not HAS_DATEUTIL:
        return None
    try:
        return parser.parse(string)
    except (ValueError, OverflowError):
        logger.warning(f'Unable to parse {string}')
    return None
