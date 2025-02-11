import json
from typing import Any, Dict, Optional

from wunderkafka.serdes.abc import AbstractDeserializer
from confluent_kafka.schema_registry.json_schema import JSONDeserializer as JSONDSchemaDeserializer


class JSONDeserializer(AbstractDeserializer):

    def __init__(self) -> None:
        self._cache: dict[str, JSONDSchemaDeserializer] = {}

    def deserialize(self, schema: str, blob: bytes, seek_pos: Optional[int] = None) -> Any:
        if schema not in self._cache:
            self._cache[schema] = JSONDSchemaDeserializer(json.dumps(json.loads(schema)))
        deserializer = self._cache[schema]
        dct = deserializer(blob, None)
        return dct
