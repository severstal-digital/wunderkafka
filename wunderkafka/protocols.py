import datetime
from typing import List, Union, Optional, Any
from typing_extensions import Protocol

from confluent_kafka import Message, TopicPartition

from wunderkafka import TopicSubscription


# ToDo (tribunsky.kir): subject to change. It's not obvious how to merge together
#                       python-kafka/confluent-kafka and out own API, so currently
#                       it's just API of (de)serializing producer/consumer with the nested 'real' producer/consumer.
from wunderkafka.types import MsgValue, MsgKey, DeliveryCallback


class AnyConsumer(Protocol):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def commit(
        self,
        message: Optional[Message] = None,
        offsets: Optional[List[TopicPartition]] = None,
        asynchronous: bool = True,
    ) -> Optional[List[TopicPartition]]:
        """Just overlap nested 'real' consumer's offset."""

    def subscribe(
        self,
        topics: List[Union[str, TopicSubscription]],
        *,
        from_beginning: Optional[bool] = None,
        offset: Optional[int] = None,
        ts: Optional[int] = None,
        with_timedelta: Optional[datetime.timedelta] = None,
    ) -> None:
        """Subscribe to a given list of topics. This replaces a previous subscription."""
        ...

    def consume(
        self,
        timeout: float = 1.0,
        num_messages: int = 1000000,
        *,
        ignore_keys: bool = False,
    ) -> List[Message]:
        """Consume as many messages as we can for a given timeout and decode them."""


class AnyProducer(Protocol):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def send_message(
            self,
            topic: str,
            value: MsgValue = None,
            key: MsgKey = None,
            partition: Optional[int] = None,
            on_delivery: Optional[DeliveryCallback] = None,
            *args: Any,
            blocking: bool = False,
            **kwargs: Any,
    ) -> None:
        """Send encoded message to Kafka almost immediately."""

    def set_target_topic(self, topic: str, value: Any, key: Any = None, *, lazy: bool = False) -> None:
        """Make producer aware how it should work with specific topic."""

    def flush(self, timeout: Optional[float] = None) -> int:
        """Just overlap nested 'real' producer's flush."""
