from typing import Dict, Optional, Any, Callable

from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer as JSONSchemaSerializer
from confluent_kafka.serialization import SerializationContext, MessageField

from wunderkafka.serdes.abc import AbstractSerializer

ConfluentAPI = Callable[[Any, SerializationContext], Dict]


def passer(obj: Any, _: SerializationContext) -> Dict:
    if isinstance(obj, dict):
        return obj
    return dict(obj)


class JSONSerializer(AbstractSerializer):
    def __init__(self, schema_registry_client: SchemaRegistryClient, to_dict: ConfluentAPI = passer) -> None:
        self._cache: Dict[str, JSONSchemaSerializer] = {}
        self._sr_client = schema_registry_client
        self._to_dict = to_dict

    def serialize(
        self,
        schema: str,
        obj: Any,
        header: Optional[bytes] = None,
        topic: Optional[str] = None,
        *,
        is_key: Optional[bool] = None,
    ) -> bytes:
        if schema not in self._cache:
            self._cache[schema] = JSONSchemaSerializer(schema, self._sr_client, self._to_dict)
        serializer = self._cache[schema]
        field = MessageField.KEY if is_key else MessageField.VALUE
        return serializer(obj, SerializationContext(topic, field))
