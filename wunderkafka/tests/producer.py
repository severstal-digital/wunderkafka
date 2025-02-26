from dataclasses import dataclass
from typing import Any, Optional, Union

from wunderkafka.callbacks import error_callback
from wunderkafka.producers.bytes import BytesProducer
from wunderkafka.types import DeliveryCallback


@dataclass
class Message:
    topic: str
    value: Optional[Union[str, bytes]]
    key: Optional[Union[str, bytes]]


class TestProducer(BytesProducer):

    def __init__(self) -> None:
        self.sent: list[Message] = []

    def send_message(
        self,
        topic: str,
        value: Optional[Union[str, bytes]] = None,
        key: Optional[Union[str, bytes]] = None,
        partition: Optional[int] = None,
        on_delivery: Optional[DeliveryCallback] = error_callback,
        *args: Any,
        blocking: bool = False,
        **kwargs: Any,
    ) -> None:
        message = Message(topic, value, key)
        self.sent.append(message)
