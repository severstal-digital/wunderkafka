from typing import Optional, Dict

from wunderkafka import ProducerConfig, BytesProducer, ConsumerConfig, BytesConsumer
from wunderkafka.consumers.constructor import HighLevelDeserializingConsumer
from wunderkafka.hotfixes.watchdog import check_watchdog
from wunderkafka.producers.constructor import HighLevelSerializingProducer
from wunderkafka.serdes.schemaless.json.deserializers import SchemaLessJSONDeserializer
from wunderkafka.serdes.schemaless.json.serializers import SchemaLessJSONSerializer
from wunderkafka.serdes.schemaless.jsonmodel.serializers import SchemaLessJSONModelSerializer
from wunderkafka.serdes.schemaless.string.deserializers import StringDeserializer
from wunderkafka.serdes.schemaless.string.serializers import StringSerializer
from wunderkafka.types import TopicName, MessageDescription


class SchemaLessJSONStringProducer(HighLevelSerializingProducer):
    """Kafka Producer client to serialize and send any value as JSON without any schema."""

    def __init__(
        self,
        mapping: Optional[Dict[TopicName, MessageDescription]],
        config: ProducerConfig,
    ) -> None:
        """
        Init producer from pre-defined blocks.

        :param mapping:     Topic-to-Schemas mapping.
                            Mapping's value should contain at least message's value schema to be used for serialization.
        :param config:      Configuration for:

                                - Librdkafka producer.
                                - Schema registry client (conventional options for HTTP).

                            Refer original CONFIGURATION.md (https://git.io/JmgCl) or generated config.
        """
        config, watchdog = check_watchdog(config)
        super().__init__(
            producer=BytesProducer(config, watchdog),
            schema_registry=None,
            header_packer=None,
            value_serializer=SchemaLessJSONSerializer(),
            key_serializer=StringSerializer(),
            mapping=mapping,
        )


class SchemaLessJSONModelStringProducer(HighLevelSerializingProducer):
    """Kafka Producer client to serialize and send any instance of pydantic model as JSON without any schema."""

    def __init__(
        self,
        mapping: Optional[Dict[TopicName, MessageDescription]],
        config: ProducerConfig,
    ) -> None:
        """
        Init producer from pre-defined blocks.

        :param mapping:     Topic-to-Schemas mapping.
                            Mapping's value should contain at least message's value schema to be used for serialization.
        :param config:      Configuration for:

                                - Librdkafka producer.
                                - Schema registry client (conventional options for HTTP).

                            Refer original CONFIGURATION.md (https://git.io/JmgCl) or generated config.
        """

        config, watchdog = check_watchdog(config)
        super().__init__(
            producer=BytesProducer(config, watchdog),
            schema_registry=None,
            header_packer=None,
            value_serializer=SchemaLessJSONModelSerializer(),
            key_serializer=StringSerializer(),
            mapping=mapping,
        )


class SchemaLessJSONStringConsumer(HighLevelDeserializingConsumer):
    """Kafka Consumer client to get JSON-serialized messages without any schema."""

    def __init__(self, config: ConsumerConfig) -> None:
        """
        Init consumer from pre-defined blocks.

        :param config:      Configuration for:

                                - Librdkafka consumer.
                                - Schema registry client (conventional options for HTTP).

                            Refer original CONFIGURATION.md (https://git.io/JmgCl) or generated config.
        """

        self._default_timeout: int = 60

        config, watchdog = check_watchdog(config)
        super().__init__(
            consumer=BytesConsumer(config, watchdog),
            schema_registry=None,
            headers_handler=None,
            value_deserializer=SchemaLessJSONDeserializer(),
            key_deserializer=StringDeserializer(),
            stream_result=False,
        )
