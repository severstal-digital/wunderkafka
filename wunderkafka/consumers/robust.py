import time
from typing import Dict, Tuple, Union, Optional

from confluent_kafka import Message, KafkaError, TopicPartition

from wunderkafka.errors import RobustTimeoutError
from wunderkafka.logger import logger

Offset = int
TopicName = str
Partition = int

# ToDo (tribunsky.kir): when python version allows, use MappingProxyType instead (isn't subscriptable in old pythons)
ConsumerState = Dict[Tuple[TopicName, Partition], Offset]


def prettify(msg: Message) -> str:
    return '{0} (error: {1}, partition: {2}, offset: {3}, value: {4})'.format(
        msg, msg.error(), msg.partition(), msg.offset(), msg.value(),
    )


def _validated_meta_info(msg: Message) -> Tuple[TopicName, Partition, Offset]:
    error = msg.error()
    if error is not None:
        raise ValueError("Tracker is not intended to be used with error messages from broker! ({0})".format(error))
    topic = msg.topic()
    if topic is None:
        raise RuntimeError("Couldn't get topic for message: {0}".format(prettify(msg)))
    partition = msg.partition()
    if partition is None:
        raise RuntimeError("Couldn't get partition for message: {0}".format(prettify(msg)))
    offset = msg.offset()
    if offset is None:
        raise RuntimeError("Couldn't get offset for message: {0}".format(prettify(msg)))
    return topic, partition, offset


class Tracker(object):
    __slots__ = ('_tracker', '_first_error_ts', '_first_error')

    def __init__(self) -> None:
        self._tracker: ConsumerState = {}
        self._first_error_ts: Optional[float] = None
        self._first_error: Optional[Union[KafkaError, Exception]] = None

    def track(self, msg: Message) -> None:
        topic, partition, offset = _validated_meta_info(msg)
        self._tracker[(topic, partition)] = offset
        self._clear_errors()

    def _clear_errors(self) -> None:
        self._first_error_ts = None
        self._first_error = None

    def capture(self, exc: Union[KafkaError, Exception]) -> None:
        if self._first_error is not None:
            logger.warning(
                "New error ({0}) received while the previous one ({1}) didn't recover".format(exc, self._first_error),
            )
        else:
            self._first_error = exc
            self._first_error_ts = time.perf_counter()

    def get_offset(self, tp: TopicPartition) -> Optional[Offset]:
        composite_key = (tp.topic, tp.partition)
        return self._tracker.get(composite_key)

    def check(self, timeout: Optional[float]) -> None:
        if timeout is None:
            return None
        if self._first_error_ts is None:
            return None
        if time.perf_counter() - self._first_error_ts > timeout:
            raise RobustTimeoutError(
                "Couldn't recover from error for {0} seconds. Last error: {1}".format(timeout, self._first_error),
            )
