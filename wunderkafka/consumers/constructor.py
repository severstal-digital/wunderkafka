"""
This module contains the high-level pipeline to produce messages with a nested consumer.

It is intended to be testable enough due to composition of dependencies.

All moving parts should be interchangeable in terms of schema, header and serialization handling
(for further overriding^W extending).
"""

import datetime
from typing import Any, List, Union, Optional

from confluent_kafka import Message, TopicPartition, KafkaError

from wunderkafka.consumers.robust import Tracker
from wunderkafka.errors import ConsumerException
from wunderkafka.types import HeaderParser
from wunderkafka.logger import logger
from wunderkafka.serdes.abc import AbstractDeserializer
from wunderkafka.structures import SchemaMeta, SchemaDescription
from wunderkafka.consumers.abc import AbstractConsumer, AbstractDeserializingConsumer
from wunderkafka.schema_registry.abc import AbstractSchemaRegistry
from wunderkafka.consumers.subscription import TopicSubscription


class HighLevelDeserializingConsumer(AbstractDeserializingConsumer):
    """Deserializing pipeline implementation of extended consumer."""

    __slots__ = (
        'consumer',
        '_header_parser',
        '_registry',
        '_deserializer',
        '_tracker',
    )

    def __init__(
        self,
        consumer: AbstractConsumer,
        headers_handler: HeaderParser,
        schema_registry: AbstractSchemaRegistry,
        deserializer: AbstractDeserializer,
    ):
        """
        Init consumer with specific dependencies.

        :param consumer:            Consumer implementation to receive messages.
        :param headers_handler:     Callable to parse binary headers.
        :param schema_registry:     Schema registry client.
        :param deserializer:        Message deserializer.
        """
        self.consumer = consumer
        self._header_parser = headers_handler
        self._registry = schema_registry
        self._deserializer = deserializer

        self._tracker = Tracker()

    @property
    def state(self) -> List[TopicPartition]:
        # Should return only real assignment, which doesn't change while consuming
        original = self.consumer.assignment()
        new = []
        for tp in original:
            offset = self._tracker.get(tp)
            if offset is None:
                new_tp = TopicPartition(topic=tp.topic, partition=tp.partition, offset=tp.offset)
            else:
                new_tp = TopicPartition(topic=tp.topic, partition=tp.partition, offset=offset)
            new.append(new_tp)
        return new

    def subscribe(  # noqa: D102,WPS211  # docstring inherited from superclass.
        self,
        topics: List[Union[str, TopicSubscription]],
        *,
        from_beginning: Optional[bool] = None,
        offset: Optional[int] = None,
        ts: Optional[int] = None,
        with_timedelta: Optional[datetime.timedelta] = None,
    ) -> None:
        self.consumer.subscribe(
            topics, from_beginning=from_beginning, offset=offset, ts=ts, with_timedelta=with_timedelta,
        )

    def commit(  # noqa: D102,WPS211  # docstring inherited from superclass.
        self,
        message: Optional[Message] = None,
        offsets: Optional[List[TopicPartition]] = None,
        asynchronous: bool = True,
    ) -> Optional[List[TopicPartition]]:
        if message is None and offsets is not None:
            return self.consumer.commit(offsets=offsets, asynchronous=asynchronous)
        if message is not None and offsets is None:
            return self.consumer.commit(message=message, asynchronous=asynchronous)
        # Default behavior
        return self.consumer.commit(message=message, offsets=offsets, asynchronous=asynchronous)

    def consume(
        self,
        timeout: float = 1.0,
        num_messages: int = 1000000,
        *,
        ignore_keys: bool = False,
        raise_on_error: bool = True,
        raise_on_lost: bool = True,
        robust_timeout: Optional[float] = None,
    ) -> List[Message]:
        """
        Consume as many messages as we can for a given timeout and decode them.

        :param timeout:         The maximum time to block waiting for messages. Decoding time doesn't count.
        :param num_messages:    The maximum number of messages to receive from broker.
                                Default is 1000000 which was the allowed maximum for librdkafka 1.2.
        :param ignore_keys:     If True, skip key decoding, key will be set to None. Otherwise, decode key as usual.
        :param raise_on_error:  if True, raise KafkaError form confluent_kafka library to handle in client code.
        :param raise_on_lost:   if True, check on own clocks if max.poll.interval.ms is exceeded. If so, raises
                                ConsumerException to be handled in client code.
        :param robust_timeout:  If set, then consumer will try to recover from errors without failing for specified
                                amount of seconds.
                                .. warning::
                                  This parameter is NOT intended to be used with topics where data is not coming
                                  quite often (e.g. more often than robust timeout). Because without new messages
                                  we are not sure if everything works under the hood and didn't break irretrievably.

        :raises KafkaError:     See https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#confluent_kafka.KafkaError

        :return:                A list of Message objects with decoded value() and key() (possibly empty on timeout).
        """
        self._tracker.check(robust_timeout)
        try:
            return self._consume(timeout, num_messages, ignore_keys, raise_on_error, raise_on_lost)
        except (ConsumerException, KafkaError) as exc:
            if robust_timeout is None:
                raise
            self._tracker.capture(exc)
            self.consumer = self.consumer.recreate(self.state)
            return self._consume(timeout, num_messages, ignore_keys, raise_on_error, raise_on_lost)

    def _consume(
        self,
        timeout: float,
        num_messages: int,
        ignore_keys: bool,
        raise_on_error: bool,
        raise_on_lost: bool,
    ) -> List[Message]:
        msgs = self.consumer.batch_poll(timeout, num_messages, raise_on_lost=raise_on_lost)
        return self._decoded(msgs, ignore_keys=ignore_keys, raise_on_error=raise_on_error)

    def _decoded(
        self,
        msgs: List[Message],
        *,
        ignore_keys: bool,
        raise_on_error: bool,
    ) -> Any:
        for msg in msgs:
            kafka_error = msg.error()
            # Not sure if there is any need for an option to exclude errored message from the consumed ones,
            # so there is no `else`. In case when `.error()` returns KafkaError, but `raise_on_error` is set to False,
            # `.value()` called in client code will return raw bytes with string from KafkaError,
            # e.g.
            #   b'Application maximum poll interval (300000ms) exceeded by Nms'
            if kafka_error is not None:
                logger.error(kafka_error)
                if raise_on_error:
                    raise kafka_error
            else:
                self._tracker.track(msg)

            topic = msg.topic()
            msg.set_value(self._decode(topic, msg.value()))
            if ignore_keys:
                # Yes, we lose information, but it is necessary to not get raw bytes
                # if `.key()` will be called in client code later.
                msg.set_key(None)
            else:
                msg.set_key(self._decode(topic, msg.key(), is_key=True))
        return msgs

    # Todo (tribunsky.kir): arguable: make different composition (headers, SR & deserializer united cache)
    def _decode(self, topic: str, blob: Optional[bytes], *, is_key: bool = False) -> Any:
        if blob is None:
            return None

        # Header is separate in the sake of customisation, e.g. we don't have SR and put schema directly in message
        parsed_header = self._header_parser(blob)
        schema_meta = SchemaMeta(
            topic=topic,
            is_key=is_key,
            header=parsed_header,
        )
        schema_text = self._registry.get_schema_text(schema_meta)
        schema = SchemaDescription(text=schema_text)
        # performance tradeoff: message may be long and we don't want to:
        # - copy the whole tail
        # - have implicit offset as if we read buffer when extracting header
        # so dealing with implicit offset and the whole binary string
        return self._deserializer.deserialize(schema.text, blob, seek_pos=parsed_header.size)
