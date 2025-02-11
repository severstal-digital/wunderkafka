from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Union, Optional

from wunderkafka.types import TopicName, KeySchemaDescription, ValueSchemaDescription
from wunderkafka.structures import SRMeta, ParsedHeader


class AbstractProtocolHandler(ABC):

    @abstractmethod
    def parse(self, blob: bytes) -> ParsedHeader: ...

    # ToDo (tribunsky.kir): make it symmetrical and more general
    @abstractmethod
    def pack(self, protocol_id: int, meta: SRMeta) -> bytes: ...


# ToDo (tribunsky.kir): make it parametrized generic?
class AbstractDeserializer(ABC):
    schemaless: bool = False

    @abstractmethod
    def deserialize(self, schema: str, payload: bytes, seek_pos: int | None = None) -> Any: ...


class AbstractSerializer(ABC):
    # We allow to nest store in serialized to avoid the necessity of passing it as tuples,
    # cause in general we want to split schema storing and message serialization,
    # and it's easier to compose like this.
    # Therefore, we can use Producer's single store, which was the single one on the old API,
    # but if serializer has its own store, it will be used instead.
    # Moreover, as for every serializer store may be passed manually,
    # it may be the same object or different if there is such a need.
    store: AbstractDescriptionStore | None = None

    @abstractmethod
    def serialize(
        self,
        schema: str,
        payload: Any,
        header: bytes | None = None,
        topic: str | None = None,
        *,
        is_key: bool | None = None,
    ) -> bytes:
        ...


class AbstractDescriptionStore(ABC):

    def __init__(self) -> None:
        self._values: dict[TopicName, ValueSchemaDescription] = {}
        self._keys: dict[TopicName, KeySchemaDescription] = {}

    def get(
        self,
        topic: TopicName,
        *,
        is_key: bool = False,
    ) -> ValueSchemaDescription | KeySchemaDescription | None:
        if is_key:
            return self._keys.get(topic)
        else:
            return self._values.get(topic)

    @abstractmethod
    def add(self, topic: TopicName, value: Any, key: Any) -> None:
        ...
