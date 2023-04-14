import copy
import time
from typing import Dict, Optional, Union

from confluent_kafka import Message, TopicPartition, KafkaError

from wunderkafka.errors import RobustTimeoutError
from wunderkafka.logger import logger

Offset = int
TopicName = str
Partition = int

# ToDo (tribunsky.kir): when python version allows, use MappingProxyType instead (isn't subscriptable in old pythons)
ConsumerState = Dict[TopicName, Dict[Partition, Offset]]


class Tracker(object):
    __slots__ = ('_tracker', '_first_error_ts', '_first_error')

    def __init__(self) -> None:
        self._tracker: Dict[TopicName, Dict[Partition, Offset]] = {}
        self._first_error_ts: Optional[float] = None
        self._first_error: Optional[Union[KafkaError, Exception]] = None

    @property
    def state(self) -> ConsumerState:
        return copy.deepcopy(self._tracker)

    def track(self, msg: Message) -> None:
        assert msg.error() is None

        topic = msg.topic()
        assert topic is not None
        partition = msg.partition()
        assert partition is not None
        if topic not in self._tracker:
            self._tracker[topic] = {}
        offset = msg.offset()
        assert offset is not None
        self._tracker[topic][partition] = offset
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

    def get(self, tp: TopicPartition) -> Optional[Offset]:
        topic_data = self._tracker.get(tp.topic)
        if topic_data:
            return topic_data.get(tp.partition)
        return None

    def check(self, timeout: Optional[float]) -> None:
        if timeout is None:
            return None
        if self._first_error_ts is None:
            return None
        if time.perf_counter() - self._first_error_ts > timeout:
            raise RobustTimeoutError(
                "Couldn't recover from error for {0} seconds. Last error: {1}".format(timeout, self._first_error),
            )
