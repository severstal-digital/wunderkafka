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

    @abstractmethod
    def deserialize(self, schema: str, payload: bytes, seek_pos: Optional[int] = None) -> Any: ...


class AbstractSerializer(ABC):
    @abstractmethod
    def serialize(
        self,
        schema: str,
        payload: Any,
        header: Optional[bytes] = None,
        topic: Optional[str] = None,
        *,
        is_key: Optional[bool] = None,
    ) -> bytes: ...


class AbstractDescriptionStore(ABC):

    def __init__(self) -> None:
        self._values: Dict[TopicName, ValueSchemaDescription] = {}
        self._keys: Dict[TopicName, KeySchemaDescription] = {}

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
    def add(self, topic: TopicName, value: Any, key: Any) -> None: ...
