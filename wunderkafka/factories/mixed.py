"""This module contains some ready-to-go combinations of the Consumer/Producer."""

from typing import Type, Optional, Dict

from wunderkafka import BytesConsumer, BytesProducer, ConsumerConfig, ProducerConfig
from wunderkafka.config.krb.rdkafka import config_requires_kerberos
from wunderkafka.consumers.constructor import HighLevelDeserializingConsumer
from wunderkafka.producers.constructor import HighLevelSerializingProducer
from wunderkafka.schema_registry import (
    ConfluentSRClient,
    KerberizableHTTPClient,
    SimpleCache,
)
from wunderkafka.serdes.avro import FastAvroDeserializer
from wunderkafka.serdes.avromodel.serializers import AvroModelSerializer
from wunderkafka.serdes.headers import ConfluentClouderaHeadersHandler
from wunderkafka.serdes.json.deserializers import JSONDeserializer
from wunderkafka.serdes.jsonmodel.serializers import JSONModelSerializer
from wunderkafka.serdes.schemaless.string.deserializers import StringDeserializer
from wunderkafka.serdes.schemaless.string.serializers import StringSerializer
from wunderkafka.serdes.store import AvroModelRepo
from wunderkafka.types import MessageDescription, TopicName


class AvroStringConsumer(HighLevelDeserializingConsumer):
    """Kafka Consumer client to get messages with avro-serialized values and string-serialized keys."""

    def __init__(
        self,
        config: ConsumerConfig,
        *,
        sr_client: Optional[Type[ConfluentSRClient]] = None,
    ) -> None:
        """
        Init consumer from pre-defined blocks.

        :param config:      Configuration for:

                                - Librdkafka consumer.
                                - Schema registry client (conventional options for HTTP).

                            Refer original CONFIGURATION.md (https://git.io/JmgCl) or generated config.

        :param sr_client:   Client for schema registry

        :raises ValueError: If schema registry configuration is missing.
        """
        self._default_timeout: int = 60
        sr = config.sr
        if sr is None:
            raise ValueError("Schema registry config is necessary for {0}".format(self.__class__.__name__))
        if sr_client is None:
            sr_client = ConfluentSRClient

        super().__init__(
            consumer=BytesConsumer(config),
            schema_registry=sr_client(
                KerberizableHTTPClient(sr),
                SimpleCache(),
            ),
            headers_handler=ConfluentClouderaHeadersHandler().parse,
            value_deserializer=FastAvroDeserializer(),
            key_deserializer=StringDeserializer(),
            stream_result=True,
        )


class AvroModelStringProducer(HighLevelSerializingProducer):
    """Kafka Producer client to send models as avro-serialized message values and string-serialized keys."""

    def __init__(
        self,
        mapping: Optional[Dict[TopicName, MessageDescription]],
        config: ProducerConfig,
        *,
        sr_client: Optional[Type[ConfluentSRClient]] = None,
    ) -> None:
        """
        Init producer from pre-defined blocks.

        :param mapping:     Topic-to-Schemas mapping.
                            Mapping's value should contain at least message's value model to derive schema which will
                            be used for serialization.
        :param config:      Configuration for:

                                - Librdkafka producer.
                                - Schema registry client (conventional options for HTTP).

                            Refer original CONFIGURATION.md (https://git.io/JmgCl) or generated config.

        :param sr_client:   Client for schema registry

        :raises ValueError: If schema registry configuration is missing.
        """
        self._default_timeout: int = 60
        sr = config.sr
        if sr is None:
            raise ValueError("Schema registry config is necessary for {0}".format(self.__class__.__name__))

        if sr_client is None:
            sr_client = ConfluentSRClient

        super().__init__(
            producer=BytesProducer(config),
            schema_registry=sr_client(
                KerberizableHTTPClient(
                    sr,
                    requires_kerberos=config_requires_kerberos(config),
                    cmd_kinit=config.sasl_kerberos_kinit_cmd,
                ),
                SimpleCache()),
            header_packer=ConfluentClouderaHeadersHandler().pack,
            value_serializer=AvroModelSerializer(AvroModelRepo()),
            key_serializer=StringSerializer(),
            mapping=mapping,
            protocol_id=0,
        )


class JSONStringConsumer(HighLevelDeserializingConsumer):
    """Kafka Consumer client to get messages with JSON-serialized values and string-serialized keys."""

    def __init__(
        self,
        config: ConsumerConfig,
        *,
        sr_client: Optional[Type[ConfluentSRClient]] = None,
    ) -> None:
        """
        Init consumer from pre-defined blocks.

        :param config:      Configuration for:

                                - Librdkafka consumer.
                                - Schema registry client (conventional options for HTTP).

                            Refer original CONFIGURATION.md (https://git.io/JmgCl) or generated config.

        :param sr_client:   Client for schema registry

        :raises ValueError: If schema registry configuration is missing.
        """
        self._default_timeout: int = 60
        sr = config.sr
        if sr is None:
            raise ValueError("Schema registry config is necessary for {0}".format(self.__class__.__name__))
        if sr_client is None:
            sr_client = ConfluentSRClient

        super().__init__(
            consumer=BytesConsumer(config),
            schema_registry=sr_client(
                KerberizableHTTPClient(sr),
                SimpleCache(),
            ),
            headers_handler=ConfluentClouderaHeadersHandler().parse,
            value_deserializer=JSONDeserializer(),
            key_deserializer=StringDeserializer(),
            stream_result=True,
        )


class JSONModelStringProducer(HighLevelSerializingProducer):
    """Kafka Producer client to send models as JSON-serialized message values and string-serialized keys."""

    def __init__(
        self,
        mapping: Optional[Dict[TopicName, MessageDescription]],
        config: ProducerConfig,
        *,
        sr_client: Optional[Type[ConfluentSRClient]] = None,
    ) -> None:
        """
        Init producer from pre-defined blocks.

        :param mapping:     Topic-to-Schemas mapping.
                            Mapping's value should contain at least message's value model to derive schema which will
                            be used for serialization.
        :param config:      Configuration for:

                                - Librdkafka producer.
                                - Schema registry client (conventional options for HTTP).

                            Refer original CONFIGURATION.md (https://git.io/JmgCl) or generated config.

        :param sr_client:   Client for schema registry

        :raises ValueError: If schema registry configuration is missing.
        """
        self._default_timeout: int = 60

        sr = config.sr
        if sr is None:
            raise ValueError("Schema registry config is necessary for {0}".format(self.__class__.__name__))

        if sr_client is None:
            sr_client = ConfluentSRClient

        schema_registry = sr_client(
            KerberizableHTTPClient(
                sr,
                requires_kerberos=config_requires_kerberos(config),
                cmd_kinit=config.sasl_kerberos_kinit_cmd,
            ),
            SimpleCache(),
        )
        super().__init__(
            producer=BytesProducer(config),
            schema_registry=schema_registry,
            header_packer=ConfluentClouderaHeadersHandler().pack,
            value_serializer=JSONModelSerializer(schema_registry.client),
            key_serializer=StringSerializer(),
            mapping=mapping,
            protocol_id=0,
        )
