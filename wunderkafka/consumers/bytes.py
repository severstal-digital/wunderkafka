"""This module contains implementation of extended confluent-kafka Consumer's API."""

import time
import atexit
import datetime
import traceback
from typing import Dict, List, Union, Optional

from confluent_kafka import KafkaException

from wunderkafka.config.krb.rdkafka import challenge_krb_arg
from wunderkafka.types import HowToSubscribe
from wunderkafka.config import ConsumerConfig
from wunderkafka.errors import ConsumerException
from wunderkafka.logger import logger
from wunderkafka.callbacks import reset_partitions
from wunderkafka.consumers.abc import Message, AbstractConsumer
from wunderkafka.consumers.subscription import TopicSubscription
from wunderkafka.hotfixes.watchdog.types import Watchdog


class BytesConsumer(AbstractConsumer):
    """Consumer implementation of extended interface for raw messages."""

    # FixMe (tribunsky.kir): add watchdog page reference
    def __init__(self, config: ConsumerConfig, sasl_watchdog: Optional[Watchdog] = None) -> None:
        """
        Init consumer.

        :param config:          Pydantic model with librdkafka consumer's configuration.
        :param sasl_watchdog:   Callable to handle global state of kerberos auth (see Watchdog).
        """
        try:
            super().__init__(config.dict())
        except KafkaException as exc:
            logger.error(traceback.format_exc())
            config.builtin_features = challenge_krb_arg(exc, config)
            super().__init__(config.dict())
        self.subscription_offsets: Optional[Dict[str, HowToSubscribe]] = None

        self._config = config
        self._last_poll_ts = time.perf_counter()
        self._sasl_watchdog = sasl_watchdog
        # ToDo (tribunsky-kir): make it configurable
        atexit.register(self.close)

    def __str__(self) -> str:
        """
        Get human-readable representation of consumer.

        :return:    string with consumer gid.
        """
        return '{0}:{1}'.format(self.__class__.__name__, self._config.group_id)

    def batch_poll(  # noqa: D102  # inherited from superclass.
        self,
        timeout: float = 1.0,
        num_messages: int = 1000000,
        *,
        raise_on_lost: bool = False,
    ) -> List[Message]:
        if self._sasl_watchdog is not None:
            self._sasl_watchdog()

        # ToDo (tribunsky.kir): naybe it better to use on_lost callback within subscribe()
        dt = int((time.perf_counter() - self._last_poll_ts) * 1000)
        if dt > self._config.max_poll_interval_ms:
            msg = 'Exceeded max.poll.interval.ms ({0}): {1}'.format(self._config.max_poll_interval_ms, dt)

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
        topics: List[Union[str, TopicSubscription]],
        *,
        from_beginning: Optional[bool] = None,
        offset: Optional[int] = None,
        ts: Optional[int] = None,
        with_timedelta: Optional[datetime.timedelta] = None,
    ) -> None:
        subscriptions = {}
        for tpc in topics:
            if isinstance(tpc, str):
                tpc = TopicSubscription(
                    topic=tpc, from_beginning=from_beginning, offset=offset, ts=ts, with_timedelta=with_timedelta,
                )
            subscriptions[tpc.topic] = tpc.how

        # We have specific subscription at least once
        if any(subscriptions.values()):
            self.subscription_offsets = subscriptions
            # ToDo (tribunsky.kir): avoid mutation of self.subscription_offset and remove it as a field
            super().subscribe(topics=list(self.subscription_offsets), on_assign=reset_partitions)
        else:
            super().subscribe(topics=list(subscriptions))
