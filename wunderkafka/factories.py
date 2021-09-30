"""This module contains some ready-to-go combinations of the Consumer/Producer."""

from typing import Dict, Optional

from wunderkafka import ConsumerConfig, ProducerConfig
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
from wunderkafka.config.schema_registry import ClouderaSRConfig


class AvroConsumer(HighLevelDeserializingConsumer):
    """Kafka Consumer client to get AVRO-serialized messages from Confluent/Cloudera installation."""

    def __init__(self, config: ConsumerConfig, sr_config: ClouderaSRConfig) -> None:
        """
        Init consumer from pre-defined blocks.

        :param config:      configuration for librdkafka consumer.
                            Refer original CONFIGURATION.md (https://git.io/JmgCl) or generated config.
        :param sr_config:   configuration for schema registry client (conventional options for HTTP).
        """
        config, watchdog = check_watchdog(config)
        super().__init__(
            consumer=BytesConsumer(config, watchdog),
            schema_registry=ClouderaSRClient(KerberizableHTTPClient(sr_config), SimpleCache()),
            headers_handler=ConfluentClouderaHeadersHandler().parse,
            deserializer=FastAvroDeserializer(),
        )


class AvroProducer(HighLevelSerializingProducer):
    """Kafka Producer client to serialize and send dictionaries or built-in types as messages."""

    def __init__(
        self,
        mapping: Optional[Dict[TopicName, MessageDescription]],
        config: ProducerConfig,
        sr_config: ClouderaSRConfig,
    ) -> None:
        """
        Init producer from pre-defined blocks.

        :param mapping:     Topic-to-Schemas mapping.
                            Mapping's value should contain at least message's value schema to be used fo serialization.
        :param config:      configuration for librdkafka producer.
                            Refer original CONFIGURATION.md (https://git.io/JmgCl) or generated config.
        :param sr_config:   configuration for schema registry client (conventional options for HTTP).
        """
        config, watchdog = check_watchdog(config)
        super().__init__(
            producer=BytesProducer(config),
            schema_registry=ClouderaSRClient(KerberizableHTTPClient(sr_config), SimpleCache()),
            header_packer=ConfluentClouderaHeadersHandler().pack,
            serializer=FastAvroSerializer(),
            store=SchemaTextRepo(),
            mapping=mapping,
        )


class AvroModelProducer(HighLevelSerializingProducer):
    """Kafka Producer client to serialize and send models or dataclasses as messages."""

    def __init__(
        self,
        mapping: Optional[Dict[TopicName, MessageDescription]],
        config: ProducerConfig,
        sr_config: ClouderaSRConfig,
    ) -> None:
        """
        Init producer from pre-defined blocks.

        :param mapping:     Topic-to-Schemas mapping.
                            Mapping's value should contain at least message's value model to derive schema which will
                            be used fo serialization.
        :param config:      configuration for librdkafka producer.
                            Refer original CONFIGURATION.md (https://git.io/JmgCl) or generated config.
        :param sr_config:   configuration for schema registry client (conventional options for HTTP).
        """
        config, watchdog = check_watchdog(config)
        super().__init__(
            producer=BytesProducer(config),
            schema_registry=ClouderaSRClient(KerberizableHTTPClient(sr_config), SimpleCache()),
            header_packer=ConfluentClouderaHeadersHandler().pack,
            serializer=AvroModelSerializer(),
            store=AvroModelRepo(),
            mapping=mapping,
        )
