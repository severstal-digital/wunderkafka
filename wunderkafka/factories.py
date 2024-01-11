"""This module contains some ready-to-go combinations of the Consumer/Producer."""

from typing import Dict, Type, Union, Optional

from wunderkafka import ConsumerConfig, ProducerConfig
from wunderkafka.config.krb.rdkafka import config_requires_kerberos
from wunderkafka.types import TopicName, MessageDescription
from wunderkafka.serdes.avro import (
    FastAvroSerializer,
    AvroModelSerializer,
    FastAvroDeserializer,
    ConfluentClouderaHeadersHandler,
)
from wunderkafka.serdes.store import AvroModelRepo, SchemaTextRepo
from wunderkafka.consumers.bytes import BytesConsumer
from wunderkafka.producers.bytes import BytesProducer
from wunderkafka.schema_registry import SimpleCache, ClouderaSRClient, KerberizableHTTPClient
from wunderkafka.hotfixes.watchdog import check_watchdog
from wunderkafka.consumers.constructor import HighLevelDeserializingConsumer
from wunderkafka.producers.constructor import HighLevelSerializingProducer
from wunderkafka.schema_registry.clients.confluent import ConfluentSRClient


class AvroConsumer(HighLevelDeserializingConsumer):
    """Kafka Consumer client to get AVRO-serialized messages from Confluent/Cloudera installation."""

    def __init__(
        self,
        config: ConsumerConfig,
        *,
        sr_client: Optional[Union[Type[ClouderaSRClient], Type[ConfluentSRClient]]] = None,
    ) -> None:
        """
        Init consumer from pre-defined blocks.

        :param config:      configuration for:
                                - librdkafka consumer.
                                - schema registry client (conventional options for HTTP).

                            Refer original CONFIGURATION.md (https://git.io/JmgCl) or generated config.

        :param sr_client:   Client for schema registry

        :raises ValueError: if schema registry configuration is missing.
        """
        sr = config.sr
        self._default_timeout: int = 60
        if sr is None:
            raise ValueError('Schema registry config is necessary for {0}'.format(self.__class__.__name__))
        if sr_client is None:
            sr_client = ClouderaSRClient

        config, watchdog = check_watchdog(config)
        super().__init__(
            consumer=BytesConsumer(config, watchdog),
            schema_registry=sr_client(
                KerberizableHTTPClient(config),
                SimpleCache(),
            ),
            headers_handler=ConfluentClouderaHeadersHandler().parse,
            deserializer=FastAvroDeserializer(),
        )


class AvroProducer(HighLevelSerializingProducer):
    """Kafka Producer client to serialize and send dictionaries or built-in types as messages."""

    def __init__(
        self,
        mapping: Optional[Dict[TopicName, MessageDescription]],
        config: ProducerConfig,
        *,
        sr_client: Optional[Union[Type[ClouderaSRClient], Type[ConfluentSRClient]]] = None,
        protocol_id: int = 1
    ) -> None:
        """
        Init producer from pre-defined blocks.

        :param mapping:     Topic-to-Schemas mapping.
                            Mapping's value should contain at least message's value schema to be used fo serialization.
        :param config:      configuration for:
                                - librdkafka producer.
                                - schema registry client (conventional options for HTTP).

                            Refer original CONFIGURATION.md (https://git.io/JmgCl) or generated config.

        :param sr_client:   Client for schema registry
        :param protocol_id: Protocol id for producer (1 - Cloudera, 0 - Confluent, etc.)

        :raises ValueError: if schema registry configuration is missing.
        """
        sr = config.sr
        if sr is None:
            raise ValueError('Schema registry config is necessary for {0}'.format(self.__class__.__name__))
        if sr_client is None:
            sr_client = ClouderaSRClient
        self._default_timeout: int = 60

        config, watchdog = check_watchdog(config)
        super().__init__(
            producer=BytesProducer(config, watchdog),
            schema_registry=sr_client(
                KerberizableHTTPClient(config),
                SimpleCache(),
            ),
            header_packer=ConfluentClouderaHeadersHandler().pack,
            serializer=FastAvroSerializer(),
            store=SchemaTextRepo(),
            mapping=mapping,
            protocol_id=protocol_id
        )


class AvroModelProducer(HighLevelSerializingProducer):
    """Kafka Producer client to serialize and send models or dataclasses as messages."""

    def __init__(
        self,
        mapping: Optional[Dict[TopicName, MessageDescription]],
        config: ProducerConfig,
        *,
        sr_client: Optional[Union[Type[ClouderaSRClient], Type[ConfluentSRClient]]] = None,
        protocol_id: int = 1
    ) -> None:
        """
        Init producer from pre-defined blocks.

        :param mapping:     Topic-to-Schemas mapping.
                            Mapping's value should contain at least message's value model to derive schema which will
                            be used fo serialization.
        :param config:      configuration for:
                                - librdkafka producer.
                                - schema registry client (conventional options for HTTP).

                            Refer original CONFIGURATION.md (https://git.io/JmgCl) or generated config.

        :param sr_client:   Client for schema registry
        :param protocol_id: Protocol id for producer (1 - Cloudera, 0 - Confluent, etc.)

        :raises ValueError: if schema registry configuration is missing.
        """
        sr = config.sr
        if sr is None:
            raise ValueError('Schema registry config is necessary for {0}'.format(self.__class__.__name__))

        if sr_client is None:
            sr_client = ClouderaSRClient
        self._default_timeout: int = 60

        config, watchdog = check_watchdog(config)
        super().__init__(
            producer=BytesProducer(config, watchdog),
            schema_registry=sr_client(
                KerberizableHTTPClient(config),
                SimpleCache(),
            ),
            header_packer=ConfluentClouderaHeadersHandler().pack,
            serializer=AvroModelSerializer(),
            store=AvroModelRepo(),
            mapping=mapping,
            protocol_id=protocol_id
        )


class AvroConfluentConsumer(AvroConsumer):
    """Kafka Consumer client to get AVRO-serialized messages from Confluent installation."""

    def __init__(self, config: ConsumerConfig):
        super().__init__(config, sr_client=ConfluentSRClient)


class AvroClouderaConsumer(AvroConsumer):
    """Kafka Consumer client to get AVRO-serialized messages from Cloudera installation."""

    def __init__(self, config: ConsumerConfig):
        super().__init__(config, sr_client=ClouderaSRClient)


class AvroModelConfluentProducer(AvroModelProducer):
    """Kafka Confluent Producer client to serialize and send models or dataclasses as messages."""

    def __init__(self, mapping: Optional[Dict[TopicName, MessageDescription]], config: ProducerConfig):
        super().__init__(mapping, config, sr_client=ConfluentSRClient, protocol_id=0)


class AvroModelClouderaProducer(AvroModelProducer):
    """Kafka Cloudera Producer client to serialize and send models or dataclasses as messages."""

    def __init__(self, mapping: Optional[Dict[TopicName, MessageDescription]], config: ProducerConfig):
        super().__init__(mapping, config, sr_client=ClouderaSRClient, protocol_id=1)
