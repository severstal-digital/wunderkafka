"""This module contains implementation of extended confluent-kafka Consumer's API."""

import time
import atexit
import datetime
from typing import Dict, List, Union, Optional, TypeVar, Callable

import confluent_kafka
from confluent_kafka import KafkaException, Consumer

from wunderkafka.config.krb.rdkafka import challenge_krb_arg
from wunderkafka.types import HowToSubscribe
from wunderkafka.config import ConsumerConfig
from wunderkafka.errors import ConsumerException
from wunderkafka.logger import logger
from wunderkafka.callbacks import reset_partitions
from wunderkafka.consumers.abc import Message, AbstractConsumer
from wunderkafka.consumers.subscription import TopicSubscription


class BytesConsumer(AbstractConsumer):
    """Consumer implementation of extended interface for raw messages."""

    def __init__(self, config: ConsumerConfig) -> None:
        """
        Init consumer.

        :param config:          Pydantic BaseSettings model with librdkafka consumer's configuration.
        """
        try:
            super().__init__(config.dict())
        except KafkaException as exc:
            config = challenge_krb_arg(exc, config)
            super().__init__(config.dict())
        self.subscription_offsets: Optional[dict[str, HowToSubscribe]] = None

        self._config = config
        self._last_poll_ts = time.perf_counter()
        # ToDo (tribunsky-kir): make it configurable
        atexit.register(self.close)

    def __str__(self) -> str:
        """
        Get human-readable representation of consumer.

        :return:    string with consumer gid.
        """
        return f'{self.__class__.__name__}:{self._config.group_id}'

    def batch_poll(  # noqa: D102 # inherited from superclass.
        self,
        timeout: float = 1.0,
        num_messages: int = 1000000,
        *,
        raise_on_lost: bool = False,
    ) -> list[Message]:

        # ToDo (tribunsky.kir): naybe it better to use on_lost callback within subscribe()
        dt = int((time.perf_counter() - self._last_poll_ts) * 1000)
        if dt > self._config.max_poll_interval_ms:
            msg = f'Exceeded max.poll.interval.ms ({self._config.max_poll_interval_ms}): {dt}'

            if raise_on_lost:
                # ToDo (tribunsky.kir): resubscribe by ts?
                raise ConsumerException(msg)
            logger.warning(msg)

        msgs = self.consume(num_messages=num_messages, timeout=timeout)
        self._last_poll_ts = time.perf_counter()
        return msgs

    # ToDo (tribunsky.kir): do not override original API and wrap it in superclass
    def subscribe(  # noqa: D102,WPS211  # inherited from superclass.
        self,
        topics: list[Union[str, TopicSubscription]],
        *,
        from_beginning: Optional[bool] = None,
        offset: Optional[int] = None,
        ts: Optional[int] = None,
        with_timedelta: Optional[datetime.timedelta] = None,
    ) -> None:
        """
        Subscribe to a list of topics, or a list of specific TopicSubscriptions.

        This method overrides original `subscribe()` method of `confluent-kafka.Consumer` and allows to subscribe
        to topic via specific offset or timestamp.

        .. warning::
            Currently this method doesn't allow to pass callbacks and uses it's own to reset partitions.
        """  # noqa: E501
        subscriptions = {}
        for tpc in topics:
            if isinstance(tpc, str):
                tpc = TopicSubscription(
                    topic=tpc, from_beginning=from_beginning, offset=offset, ts=ts, with_timedelta=with_timedelta,
                )
            subscriptions[tpc.topic] = tpc.how

        # We have a specific subscription at least once
        if any(subscriptions.values()):
            self.subscription_offsets = subscriptions
            # ToDo (tribunsky.kir): avoid mutation of self.subscription_offset and remove it as a field
            super().subscribe(topics=list(self.subscription_offsets), on_assign=reset_partitions)
        else:
            super().subscribe(topics=list(subscriptions))


T = TypeVar('T')


def _patched_docstring(method: Callable[..., T], parent_method: Callable[..., T]) -> Optional[str]:
    current_doc = method.__doc__
    if not current_doc:
        return None
    first, *_ = (line for line in current_doc.split('\n') if line)
    spaces = 0
    for ch in first:
        if ch != ' ':
            break
        spaces += 1
    prefix = ' ' * spaces
    disclaimer = " ".join([
        "Doc of an original method depends on python's :code:`confluent-kafka` version.",
        "Please, refer to `confluent-kafka documentation",
        "<https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#pythonclient-consumer>`__.",  # noqa: E501
    ])
    version_notes = [
        disclaimer,
        f"Below is the version rendered for version **{confluent_kafka.__version__}**:",
    ]
    version_note = '\n\n'.join(prefix + note for note in version_notes)
    original_doc = parent_method.__doc__ or ''
    intended = []
    if original_doc:
        original_doc_lines = original_doc.split('\n')
        for line in original_doc_lines:
            if line:
                intended.append(prefix + line)
            else:
                intended.append(line)
        original_doc = '\n\n{}'.format('\n'.join(intended))
    return f'{current_doc}\n{version_note}{original_doc}'


BytesConsumer.subscribe.__doc__ = _patched_docstring(BytesConsumer.subscribe, Consumer.subscribe)
