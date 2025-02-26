from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional, Union

from wunderkafka.structures import ParsedHeader, SRMeta
from wunderkafka.types import KeySchemaDescription, TopicName, ValueSchemaDescription


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
    def deserialize(self, schema: str, payload: bytes, seek_pos: Optional[int] = None) -> Any: ...


class AbstractSerializer(ABC):
    # We allow to nest store in serialized to avoid the necessity of passing it as tuples,
    # cause in general we want to split schema storing and message serialization,
    # and it's easier to compose like this.
    # Therefore, we can use Producer's single store, which was the single one on the old API,
    # but if serializer has its own store, it will be used instead.
    # Moreover, as for every serializer store may be passed manually,
    # it may be the same object or different if there is such a need.
    store: Optional[AbstractDescriptionStore] = None

    @abstractmethod
    def serialize(
        self,
        schema: str,
        payload: Any,
        header: Optional[bytes] = None,
        topic: Optional[str] = None,
        *,
        is_key: Optional[bool] = None,
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
    ) -> Optional[Union[ValueSchemaDescription, KeySchemaDescription]]:
        if is_key:
            return self._keys.get(topic)
        else:
            return self._values.get(topic)

    @abstractmethod
    def add(self, topic: TopicName, value: Any, key: Any) -> None:
        ...
