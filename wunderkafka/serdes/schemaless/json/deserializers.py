import json
from typing import Any, Dict, Optional

from wunderkafka.serdes.abc import AbstractDeserializer
from confluent_kafka.schema_registry.json_schema import JSONDeserializer as JSONDSchemaDeserializer


class SchemaLessJSONDeserializer(AbstractDeserializer):

    def __init__(self) -> None:
        self.schemaless = True
        self._cache: Dict[str, JSONDSchemaDeserializer] = {}

    def deserialize(self, schema: str, blob: bytes, seek_pos: Optional[int] = None) -> Any:
        return json.loads(blob)