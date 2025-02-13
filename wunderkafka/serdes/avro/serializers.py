import io
from json import loads
from typing import Any, Optional

from fastavro import parse_schema, schemaless_writer

from wunderkafka.serdes.abc import AbstractSerializer, AbstractDescriptionStore
from wunderkafka.serdes.avro.types import FastAvroParsedSchema


class FastAvroSerializer(AbstractSerializer):
    def __init__(self, store: Optional[AbstractDescriptionStore] = None) -> None:
        self._cache: dict[str, FastAvroParsedSchema] = {}
        self.store = store

    def serialize(
        self,
        schema: str,
        payload: Any,
        header: Optional[bytes] = None,
        topic: Optional[str] = None,
        *,
        is_key: Optional[bool] = None,
    ) -> bytes:
        if schema not in self._cache:
            self._cache[schema] = parse_schema(loads(schema))
        writer_schema = self._cache[schema]
        with io.BytesIO() as buffer:
            if header is not None:
                buffer.write(header)
            schemaless_writer(buffer, writer_schema, payload)
            return buffer.getvalue()
