"""
Module contains interface-like skeletons for producer.

- inherited from confluent-kafka Producer to use it as nested entity
- high-level producer which is able to handle message's schemas
"""


from abc import ABC, abstractmethod
from typing import Any, Union, Optional

from confluent_kafka import Producer

from wunderkafka.types import MsgKey, MsgValue, DeliveryCallback


class AbstractProducer(Producer):
    """Extension point for the original Producer API."""

    def send_message(  # noqa: WPS211  # ToDo (tribunsky.kir): rethink API?
        self,
        topic: str,
        value: Optional[Union[str, bytes]] = None,  # noqa: WPS110  # Domain.
        key: Optional[Union[str, bytes]] = None,
        partition: Optional[int] = None,
        on_delivery: Optional[DeliveryCallback] = None,
        *args: Any,
        blocking: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Send encoded message to Kafka almost immediately.

        This method overlaps original producers' method.

        :param topic:           Target topic against which we are working for this call.
        :param value:           Message's value encoded object to be sent.
        :param key:             Message's key encoded object to be sent.
        :param partition:       Target partition to produce to. If none, uses configured built-in
                                partitioner by default.
        :param on_delivery:     Callback to be executed on successful/failed delivery.
        :param args:            Other positional arguments to call with original produce() API.
        :param blocking:        If True, will block execution until delivery result retrieved
                                (calls flush() under the hood). Otherwise, will produce message to
                                built-in queue and call poll() to trigger producer's events.
        :param kwargs:          Other keyword arguments to call with original produce() API.


        ..  # noqa: DAR401
        """
        raise NotImplementedError


class AbstractSerializingProducer(ABC):
    """High-level interface for extended producer."""

    @abstractmethod
    def send_message(  # noqa: WPS211  # overlaps API from AbstractProducer, maybe should be mixin.
        self,
        topic: str,
        value: MsgValue = None,  # noqa: WPS110  # Domain, overlaps API from AbstractProducer
        key: MsgKey = None,
        partition: Optional[int] = None,
        on_delivery: Optional[DeliveryCallback] = None,
        *args: Any,
        blocking: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Encode and send message to Kafka.

        This method overlaps AbstractProducer's method and intended to use produce() of real nested producer.

        :param topic:           Target topic against which we are working for this call.
        :param value:           Message's value object to be encoded and sent.
        :param key:             Message's key object to be encoded and sent.
        :param partition:       Target partition to produce to. If none, uses configured built-in
                                partitioner by default.
        :param on_delivery:     Callback to be executed on successful/failed delivery.
        :param args:            Other positional arguments to call with original produce() API.
        :param blocking:        If True, will block execution until delivery result retrieved
                                (calls flush() under the hood). Otherwise, will produce message to
                                built-in queue and call poll() to trigger producer's events.
        :param kwargs:          Other keyword arguments to call with original produce() API.
        """

    # ToDo (tribunsky.kir): change naming. It is like subscribe, but publish/add_topic whatever
    @abstractmethod
    def set_target_topic(self, topic: str, value: Any, key: Any = None, *, lazy: bool = False) -> None:  # noqa: WPS110
        """
        Make producer aware how it should work with specific topic.

        This method is used to instantiate producer with mapping, but also add schemas in runtime.

        :param topic:           Target topic to specify schema description against.
        :param value:           Message's value schema description.
        :param key:             Message's key schema description.
        :param lazy:            If True, do not register schema in registry during __init__,
                                or before the first attempt to send message for a given topic.
                                Otherwise, register schema immediately.
        """

    @abstractmethod
    def flush(self, timeout: float) -> int:
        """
        Wait for all messages in the Producer queue to be delivered.

        This method overlaps original producers' method and will use the nested producer.

        :param timeout:         Maximum time to block.
        :return:                Number of messages still in queue.
        """
