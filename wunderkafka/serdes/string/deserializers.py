from typing import Any, Optional

from confluent_kafka.serialization import StringDeserializer as _StringDeserializer

from wunderkafka.serdes.abc import AbstractDeserializer


class StringDeserializer(AbstractDeserializer):
    def __init__(self) -> None:
        self.schemaless = True
        self._deserializer = _StringDeserializer()

    def deserialize(self, schema: str, blob: bytes, seek_pos: Optional[int] = None) -> Any:
        return self._deserializer(blob, None)
