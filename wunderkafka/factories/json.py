"""This module contains some ready-to-go combinations of the Consumer/Producer."""

from typing import Union, Optional

from wunderkafka import ConsumerConfig, ProducerConfig
from wunderkafka.types import TopicName, MessageDescription
from wunderkafka.structures import SchemaType
from wunderkafka.serdes.store import JSONModelRepo, SchemaTextRepo
from wunderkafka.serdes.headers import ConfluentClouderaHeadersHandler
from wunderkafka.consumers.bytes import BytesConsumer
from wunderkafka.producers.bytes import BytesProducer
from wunderkafka.schema_registry import SimpleCache, ClouderaSRClient, KerberizableHTTPClient
from wunderkafka.config.krb.rdkafka import config_requires_kerberos
from wunderkafka.consumers.constructor import HighLevelDeserializingConsumer
from wunderkafka.producers.constructor import HighLevelSerializingProducer
from wunderkafka.serdes.json.serializers import JSONSerializer
from wunderkafka.serdes.json.deserializers import JSONDeserializer
from wunderkafka.serdes.jsonmodel.serializers import JSONModelSerializer
from wunderkafka.schema_registry.clients.confluent import ConfluentSRClient


class JSONConsumer(HighLevelDeserializingConsumer):
    """Kafka Consumer client to get JSON-serialized messages from Confluent/Cloudera installation."""

    def __init__(
        self,
        config: ConsumerConfig,
        *,
        sr_client: Optional[Union[type[ClouderaSRClient], type[ConfluentSRClient]]] = None,
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
        sr = config.sr
        self._default_timeout: int = 60
        if sr is None:
            raise ValueError(f'Schema registry config is necessary for {self.__class__.__name__}')
        if sr_client is None:
            sr_client = ClouderaSRClient

        super().__init__(
            consumer=BytesConsumer(config),
            schema_registry=sr_client(
                KerberizableHTTPClient(
                    sr,
                    requires_kerberos=config_requires_kerberos(config),
                    cmd_kinit=config.sasl_kerberos_kinit_cmd,
                ),
                SimpleCache(),
            ),
            headers_handler=ConfluentClouderaHeadersHandler().parse,
            deserializer=JSONDeserializer(),
        )


class JSONProducer(HighLevelSerializingProducer):
    """Kafka Producer client to serialize and send dictionaries or built-in types as messages."""

    def __init__(
        self,
        mapping: Optional[dict[TopicName, MessageDescription]],
        config: ProducerConfig,
        *,
        sr_client: Optional[type[ConfluentSRClient]] = None,
        protocol_id: int = 1
    ) -> None:
        """
        Init producer from pre-defined blocks.

        :param mapping:     Topic-to-Schemas mapping.
                            Mapping's value should contain at least message's value schema to be used for serialization.
        :param config:      Configuration for:

                                - Librdkafka producer.
                                - Schema registry client (conventional options for HTTP).

                            Refer original CONFIGURATION.md (https://git.io/JmgCl) or generated config.

        :param sr_client:   Client for schema registry
        :param protocol_id: Protocol id for producer (1 - Cloudera, 0 - Confluent, etc.)

        :raises ValueError: If schema registry configuration is missing.
        """
        sr = config.sr
        if sr is None:
            raise ValueError(f'Schema registry config is necessary for {self.__class__.__name__}')
        if sr_client is None:
            sr_client = ConfluentSRClient
        self._default_timeout: int = 60

        schema_registry = sr_client(
            KerberizableHTTPClient(
                sr, requires_kerberos=config_requires_kerberos(config), cmd_kinit=config.sasl_kerberos_kinit_cmd,
            ),
            SimpleCache(),
        )
        super().__init__(
            producer=BytesProducer(config),
            schema_registry=schema_registry,
            header_packer=ConfluentClouderaHeadersHandler().pack,
            serializer=JSONSerializer(schema_registry.client),
            store=SchemaTextRepo(schema_type=SchemaType.JSON),
            mapping=mapping,
            protocol_id=protocol_id
        )


class JSONModelProducer(HighLevelSerializingProducer):
    """Kafka Producer client to serialize and send models or dataclasses as messages."""

    def __init__(
        self,
        mapping: Optional[dict[TopicName, MessageDescription]],
        config: ProducerConfig,
        *,
        sr_client: Optional[type[ConfluentSRClient]] = None,
        protocol_id: int = 1
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
        :param protocol_id: Protocol id for producer (1 - Cloudera, 0 - Confluent, etc.)

        :raises ValueError: If schema registry configuration is missing.
        """
        sr = config.sr
        if sr is None:
            raise ValueError(f'Schema registry config is necessary for {self.__class__.__name__}')

        if sr_client is None:
            sr_client = ConfluentSRClient
        self._default_timeout: int = 60

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
            serializer=JSONModelSerializer(schema_registry.client),
            store=JSONModelRepo(),
            mapping=mapping,
            protocol_id=protocol_id
        )


class JSONConfluentConsumer(JSONConsumer):
    """Kafka Consumer client to get JSON-serialized messages from Confluent installation."""

    def __init__(self, config: ConsumerConfig):
        super().__init__(config, sr_client=ConfluentSRClient)


class JSONModelConfluentProducer(JSONModelProducer):
    """Kafka Confluent Producer client to serialize and send models or dataclasses as messages."""

    def __init__(self, mapping: Optional[dict[TopicName, MessageDescription]], config: ProducerConfig):
        super().__init__(mapping, config, sr_client=ConfluentSRClient, protocol_id=0)
