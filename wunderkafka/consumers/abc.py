"""
Module contains interface-like skeletons for consumer.

- inherited from confluent-kafka Consumer to use it as nested entity
- high-level consumer which is able to handle message's schemas
"""

import datetime
from abc import ABC, abstractmethod
from typing import Dict, List, Union, Optional

from confluent_kafka import Message, Consumer, TopicPartition

from wunderkafka.types import HowToSubscribe
from wunderkafka.config import ConsumerConfig
from wunderkafka.consumers.subscription import TopicSubscription


class AbstractConsumer(Consumer):
    """Extension point for the original Consumer API."""

    # Why so: https://github.com/python/mypy/issues/4125
    _config: ConsumerConfig
    subscription_offsets: Optional[Dict[str, HowToSubscribe]] = None

    @property
    def config(self) -> ConsumerConfig:
        """
        Get the consumer's config.

        Tech Debt: needed here for specific callback which resets partition to specific offset.

        :return:        Pydantic model with librdkafka consumer's configuration.
        """
        return self._config

    def batch_poll(
        self,
        timeout: float = 1.0,
        num_messages: int = 1000000,
        *,
        raise_on_lost: bool = False,
    ) -> List[Message]:
        """
        Consume as many messages as we can for a given timeout.

        Created to allow deserializing consumer nest BytesConsumer and read messages via batches
        and not communicate with broker for every single message.

        :param timeout:         The maximum time to block waiting for message.
        :param num_messages:    The maximum number of messages to receive from broker.
                                Default is 1000000 which was the allowed maximum for librdkafka 1.2.
        :param raise_on_lost:   If True, raise exception whenever we are too late to call next poll.
                                Otherwise, will do nothing or behave depending on specified callbacks.

        :return:                A list of Message objects (possibly empty on timeout).

        ..  # noqa: DAR401
        ..  # noqa: DAR202
        """
        raise NotImplementedError


class AbstractDeserializingConsumer(ABC):
    """High-level interface for extended consumer."""

    @abstractmethod
    def commit(
        self,
        message: Optional[Message] = None,
        offsets: Optional[List[TopicPartition]] = None,
        asynchronous: bool = True,
    ) -> Optional[List[TopicPartition]]:
        """
        Commit a message or a list of offsets.

        This method overlaps original consumer's method and will use the nested consumer.

        :param message:         Commit offset (+1), extracted from Message object itself.
        :param offsets:         Commit exactly TopicPartition data.
        :param asynchronous:    If True, do not block execution, otherwise - wait until commit fail or success.

        :raises KafkaException: If all commits failed.

        :return:                On asynchronous call returns None immediately.
                                Committed offsets on synchronous call, if succeed.
        """

    @abstractmethod
    def subscribe(  # noqa: WPS211  # ToDo (tribunsky.kir): reconsider API of 'how'
        self,
        topics: List[Union[str, TopicSubscription]],
        *,
        from_beginning: Optional[bool] = None,
        offset: Optional[int] = None,
        ts: Optional[int] = None,
        with_timedelta: Optional[datetime.timedelta] = None,
    ) -> None:
        """
        Subscribe to a given list of topics. This replaces a previous subscription.

        This method overlaps original consumer's method and will use the nested consumer.

        :param topics:          List of topics to subscribe. If topic has no specific subscription, specified value
                                for beginning/end/offset/timestamp/timedelta/built-in will be used.
        :param from_beginning:  If flag is set, return specific offset corresponding to beginning/end of the topic.
        :param offset:          If set, will return Offset object.
        :param ts:              If set, will return Timestamp.
        :param with_timedelta:  If set, will calculate timestamp for corresponding timedelta.
        """
