"""This module contains subscription helpers."""

import datetime
from typing import Union, Optional

from confluent_kafka import OFFSET_END, OFFSET_BEGINNING

from wunderkafka.structures import Offset, Timestamp


def choose_offset(
    from_beginning: Optional[bool] = None,
    offset: Optional[int] = None,
    ts: Optional[float] = None,
    with_timedelta: Optional[datetime.timedelta] = None,
) -> Optional[Union[Offset, Timestamp]]:
    """
    Choose subscription method (Offset, Timestamp, None), corresponding to given values.

    :param from_beginning:  If flag is set, return specific offset corresponding to beginning/end of the topic.
    :param offset:          If set, will return Offset object.
    :param ts:              If set, will return Timestamp.
    :param with_timedelta:  If set, will calculate timestamp for corresponding timedelta.

    :raises ValueError:     If multiple values are set: there is no sense in attempt to subscribe to topic via multiple
                            offsets (excluding multiple partitions scenario, which is not currently supported).

    :return:                None if no values are specified, Offset or Timestamp otherwise.
    """
    args = (from_beginning, offset, ts, with_timedelta)
    if sum([arg is not None for arg in args]) > 1:
        raise ValueError('Only one subscription method per time is allowed!')
    if from_beginning is not None:
        offset = OFFSET_BEGINNING if from_beginning else OFFSET_END
    if offset is not None:
        return Offset(offset)
    if with_timedelta is not None:
        start = datetime.datetime.now() - with_timedelta
        ts = start.timestamp() * 1000
    if ts is not None:
        return Timestamp(int(ts))
    return None


class TopicSubscription:
    """Allows custom definition of subscription for topic without need to build full TopicPartition list."""

    def __init__(  # noqa: WPS211  # ToDo (tribunsky.kir): reconsider API of 'how'
        self,
        topic: str,
        *,
        from_beginning: Optional[bool] = None,
        offset: Optional[int] = None,
        ts: Optional[int] = None,
        with_timedelta: Optional[datetime.timedelta] = None,
    ) -> None:
        """
        Init topic subscription object.

        Only one method of subscription per topic is allowed at time:

        - from beginning (depends on your retention policy)
        - from end (consume only latest messages)
        - via specific offset
        - via specific timestamp
        - via specific timedelta (from current datetime)
        - no special option (consumer will use "default" value of auto.offset.reset)

        :param topic:           Topic to subscribe.
        :param from_beginning:  If True, subscribe to get earliest available messages. If False, get latest messages.
        :param offset:          Subscribe to specific offset.
                                If offset not found, will behave with built-in default.
        :param ts:              Subscribe to specific timestamp (milliseconds).
                                If timestamp not found, will behave with built-in default.
        :param with_timedelta:  Subscribe to some moment in the past, from current datetime for a given timedelta.
                                Will calculate specific timestamp and subscribe via ts.
        """
        self.topic = topic
        self.how = choose_offset(
            from_beginning=from_beginning, offset=offset, ts=ts, with_timedelta=with_timedelta,
        )
