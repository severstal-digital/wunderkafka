import datetime
from typing import Any, List, Union, Optional

from confluent_kafka import KafkaError

from wunderkafka.consumers.bytes import BytesConsumer
from wunderkafka.consumers.subscription import TopicSubscription


class Message:
    def __init__(self, topic: str, value: bytes, key: Optional[bytes] = None, error: Optional[KafkaError] = None):
        self._topic = topic
        self._value = value
        self._key = key
        self._error = error

    def value(self) -> bytes:
        return self._value

    def set_value(self, value: Any) -> None:
        self._value = value

    def key(self) -> Optional[bytes]:
        return self._key

    def set_key(self, key: Any) -> None:
        self._key = key

    def topic(self) -> str:
        return self._topic

    def error(self) -> Optional[KafkaError]:
        return self._error


class TestConsumer(BytesConsumer):
    def __init__(self, msgs: list[Message]) -> None:
        self._msgs = msgs

    def subscribe(
        self,
        topics: list[Union[str, TopicSubscription]],
        *,
        from_beginning: Optional[bool] = None,
        offset: Optional[int] = None,
        ts: Optional[int] = None,
        with_timedelta: Optional[datetime.timedelta] = None,
    ) -> None:
        pass

    def batch_poll(
        self,
        timeout: float = 1.0,
        num_messages: int = 1000000,
        *,
        raise_on_lost: bool = False,
    ) -> list[Message]:
        return self._msgs
