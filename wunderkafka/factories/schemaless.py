from typing import Optional, Dict

from wunderkafka import ProducerConfig, BytesProducer, ConsumerConfig, BytesConsumer
from wunderkafka.consumers.constructor import HighLevelDeserializingConsumer
from wunderkafka.hotfixes.watchdog import check_watchdog
from wunderkafka.producers.constructor import HighLevelSerializingProducer
from wunderkafka.serdes.schemaless.json.deserializers import SchemaLessJSONDeserializer
from wunderkafka.serdes.schemaless.json.serializers import SchemaLessJSONSerializer, SchemaLessJSONModelSerializer
from wunderkafka.serdes.schemaless.string.deserializers import StringDeserializer
from wunderkafka.serdes.schemaless.string.serializers import StringSerializer
from wunderkafka.types import TopicName, MessageDescription


class SchemaLessJSONStringProducer(HighLevelSerializingProducer):
    def __init__(
            self,
            mapping: Optional[Dict[TopicName, MessageDescription]],
            config: ProducerConfig,
    ) -> None:
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
    def __init__(
        self,
        mapping: Optional[Dict[TopicName, MessageDescription]],
        config: ProducerConfig,
    ) -> None:
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

    def __init__(
        self,
        config: ConsumerConfig,
    ) -> None:
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

