import io
from json import loads
from typing import Any, Optional

from fastavro import parse_schema, schemaless_reader

from wunderkafka.serdes.abc import AbstractDeserializer
from wunderkafka.serdes.avro.types import FastAvroParsedSchema


class FastAvroDeserializer(AbstractDeserializer):
    # ToDo (tribunsky.kir): it's better to cache loaded Schema earlier, but then it breaks layers.

    def __init__(self) -> None:
        self._cache: dict[str, FastAvroParsedSchema] = {}

    def deserialize(self, schema: str, blob: bytes, seek_pos: Optional[int] = None) -> Any:
        if schema not in self._cache:
            self._cache[schema] = parse_schema(loads(schema))
        reader_schema = self._cache[schema]
        with io.BytesIO(blob) as buffer:
            if seek_pos is not None:
                buffer.seek(seek_pos)
            return schemaless_reader(buffer, reader_schema, None, False)
