"""This module contains implementation of extended confluent-kafka Producer's API."""

import atexit
from typing import Any, Union, Optional

from confluent_kafka import KafkaException

from wunderkafka.config.krb.rdkafka import challenge_krb_arg
from wunderkafka.types import DeliveryCallback
from wunderkafka.config import ProducerConfig
from wunderkafka.callbacks import error_callback
from wunderkafka.producers.abc import AbstractProducer
from wunderkafka.hotfixes.watchdog.types import Watchdog


class BytesProducer(AbstractProducer):
    """Producer implementation of extended interface for raw messages."""

    # FixMe (tribunsky.kir): add watchdog page reference
    def __init__(self, config: ProducerConfig, sasl_watchdog: Optional[Watchdog] = None) -> None:
        """
        Init producer.

        :param config:          Pydantic model with librdkafka producer's configuration.
        :param sasl_watchdog:   Callable to handle global state of kerberos auth (see Watchdog).
        """
        try:
            super().__init__(config.dict())
        except KafkaException as exc:
            config = challenge_krb_arg(exc, config)
            super().__init__(config.dict())

        self._config = config
        self._sasl_watchdog = sasl_watchdog
        atexit.register(self.flush)

    # ToDo (tribunsky.kir): make inherited from RDConfig models immutable.
    #                       Currently it explodes because of mutation in watchdog.
    #                       Do we need re-initiation of consumer/producer in runtime?
    @property
    def config(self) -> ProducerConfig:
        """
        Get the producer's config.

        :return:        Pydantic model with librdkafka producer's configuration.
        """
        return self._config

    def send_message(  # noqa: D102,WPS211  # inherited from superclass.
        self,
        topic: str,
        value: Optional[Union[str, bytes]] = None,  # noqa: WPS110  # Domain. inherited from superclass.
        key: Optional[Union[str, bytes]] = None,
        partition: Optional[int] = None,
        on_delivery: Optional[DeliveryCallback] = error_callback,
        *args: Any,
        blocking: bool = False,
        timeout: int = 10,
        **kwargs: Any,
    ) -> None:
        if self._sasl_watchdog is not None:
            self._sasl_watchdog()
        if partition is not None:
            self.produce(topic, value, key=key, partition=partition, on_delivery=on_delivery, **kwargs)
        else:
            self.produce(topic, value, key=key, on_delivery=on_delivery, **kwargs)
        if blocking:
            self.flush(timeout=timeout)
        else:
            self.poll(timeout=timeout)
