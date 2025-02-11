"""Some timing boilerplate."""

import time
import datetime


def now() -> int:
    """
    Return UNIX timestamp in ms.

    :returns:        current timestamp (ms)
    """
    return int(time.time()*1000)


def ts2dt(ts: float) -> datetime.datetime:
    """
    Convert unix-timestamp to datetime object.

    :param ts:              Timestamp in seconds or milliseconds.
    :returns:               Corresponding datetime object.

    :raises ValueError:     Raised when couldn't coerce float to datetime.
    """
    ts_str_len_ms = 13      # 1559574586123
    current_ts_len = len(str(int(ts)))
    if current_ts_len <= 10:  # 155957458
        return datetime.datetime.fromtimestamp(ts)
    if current_ts_len == ts_str_len_ms:
        return datetime.datetime.fromtimestamp(round(ts/1000))
    raise ValueError(f'Invalid timestamp: {ts} seems not to be a UNIX-timestamp in seconds or milliseconds')
