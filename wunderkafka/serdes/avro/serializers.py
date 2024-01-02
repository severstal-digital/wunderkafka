import io
from json import loads
from typing import Any, Dict, Optional
from dataclasses import asdict, is_dataclass

from fastavro import parse_schema, schemaless_writer
from pydantic import BaseModel

from wunderkafka.serdes.abc import AbstractSerializer
from wunderkafka.serdes.avro.types import FastAvroParsedSchema


class FastAvroSerializer(AbstractSerializer):
    def __init__(self) -> None:
        self._cache: Dict[str, FastAvroParsedSchema] = {}

    def serialize(self, schema: str, obj: Any, header: Optional[bytes] = None) -> bytes:
        if schema not in self._cache:
            self._cache[schema] = parse_schema(loads(schema))
        writer_schema = self._cache[schema]
        with io.BytesIO() as buffer:
            if header is not None:
                buffer.write(header)
            schemaless_writer(buffer, writer_schema, obj)
            return buffer.getvalue()


class AvroModelSerializer(AbstractSerializer):

    def __init__(self) -> None:
        self._serializer = FastAvroSerializer()

    def serialize(self, schema: str, payload: Any, header: Optional[bytes] = None) -> bytes:
        if isinstance(payload, BaseModel):
            dct = payload.model_dump()
        else:
            dct = asdict(payload) if is_dataclass(payload) else dict(payload)
        return self._serializer.serialize(schema, dct, header)
