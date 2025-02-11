from typing import Any, Callable, Optional

from confluent_kafka.serialization import MessageField, SerializationContext
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer as JSONSchemaSerializer

from wunderkafka.serdes.abc import AbstractSerializer, AbstractDescriptionStore

ConfluentAPI = Callable[[Any, SerializationContext], dict]


def any_to_dict(obj: Any, _: SerializationContext) -> dict:
    if isinstance(obj, dict):
        return obj
    return dict(obj)


class JSONSerializer(AbstractSerializer):
    def __init__(
        self,
        schema_registry_client: SchemaRegistryClient,
        store: Optional[AbstractDescriptionStore] = None,
        to_dict: ConfluentAPI = any_to_dict,
    ) -> None:
        self._cache: dict[str, JSONSchemaSerializer] = {}
        self._sr_client = schema_registry_client
        self._to_dict = to_dict
        self.store = store

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
