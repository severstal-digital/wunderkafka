import time
import datetime

import pytest

from wunderkafka.consumers.subscription import Offset, Timestamp, choose_offset


def test_nothing_set() -> None:
    assert choose_offset(None, None, None, None) is None


def test_from_beginning() -> None:
    left = choose_offset(from_beginning=True)
    right = choose_offset(from_beginning=False)
    assert left != right
    assert isinstance(left, Offset)
    assert isinstance(right, Offset)


def test_set_ts() -> None:
    now = time.time() * 1000
    res = choose_offset(ts=now)
    assert isinstance(res, Timestamp)
    assert res.value == int(now)

    with pytest.raises(ValueError):
        choose_offset(ts=now, from_beginning=True)


def test_set_timedelta() -> None:
    target = time.time() - 2 * 60
    res = choose_offset(with_timedelta=datetime.timedelta(minutes=2))
    assert isinstance(res, Timestamp)
    assert res.value == pytest.approx(target*1000)

    with pytest.raises(ValueError):
        choose_offset(with_timedelta=datetime.timedelta(minutes=2), from_beginning=True)


def test_set_offset() -> None:
    target = 12345
    res = choose_offset(offset=target)
    assert res.value == target
    assert isinstance(res, Offset)
