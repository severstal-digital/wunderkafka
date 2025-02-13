import json
from typing import Any, Optional

from confluent_kafka.schema_registry.json_schema import JSONDeserializer as JSONDSchemaDeserializer

from wunderkafka.serdes.abc import AbstractDeserializer


class SchemaLessJSONDeserializer(AbstractDeserializer):

    def __init__(self) -> None:
        self.schemaless = True
        self._cache: dict[str, JSONDSchemaDeserializer] = {}

    def deserialize(self, schema: str, blob: bytes, seek_pos: Optional[int] = None) -> Any:
        return json.loads(blob)
