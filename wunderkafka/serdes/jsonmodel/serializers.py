import json
from typing import Any, Optional

from pydantic import BaseModel
from confluent_kafka.serialization import MessageField, SerializationContext
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer

from wunderkafka.serdes.abc import AbstractSerializer, AbstractDescriptionStore
from wunderkafka.serdes.store import JSONModelRepo


def pydantic_to_dict(model: BaseModel, _: SerializationContext) -> dict:
    dump = model.model_dump_json()
    dct = json.loads(dump)
    return dct


class JSONModelSerializer(AbstractSerializer):
    def __init__(
        self,
        schema_registry_client: SchemaRegistryClient,
        store: Optional[AbstractDescriptionStore] = None,
    ) -> None:
        self._cache: dict[str, JSONSerializer] = {}
        self._sr_client = schema_registry_client
        self.store = store or JSONModelRepo()

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
            self._cache[schema] = JSONSerializer(schema, self._sr_client, pydantic_to_dict)
        serializer = self._cache[schema]
        field = MessageField.KEY if is_key else MessageField.VALUE
        return serializer(obj, SerializationContext(topic, field))
