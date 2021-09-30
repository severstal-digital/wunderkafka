import time
import datetime

import pytest

from wunderkafka.time import ts2dt


def test_invalid_ts():
    with pytest.raises(ValueError):
        ts2dt(time.time()*1000000)


def test_seconds():
    dt = datetime.datetime.now()
    assert ts2dt(dt.timestamp()) == dt


def test_ms():
    dt = datetime.datetime.now()
    assert ts2dt(dt.timestamp()*1000) - dt.replace(microsecond=0) <= datetime.timedelta(seconds=1)
