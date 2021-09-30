from typing import Type, Optional

from wunderkafka.types import TopicName, KeySchemaDescription, ValueSchemaDescription
from wunderkafka.serdes.abc import AbstractDescriptionStore
from wunderkafka.compat.types import AvroModel
from wunderkafka.compat.constants import PY36
from wunderkafka.serdes.avromodel import derive


class SchemaTextRepo(AbstractDescriptionStore):

    def add(self, topic: TopicName, value: str, key: str) -> None:
        self._values[topic] = ValueSchemaDescription(text=value)
        if key is not None:
            self._keys[topic] = KeySchemaDescription(text=value)


class AvroModelRepo(AbstractDescriptionStore):

    def __init__(self) -> None:
        super().__init__()
        if PY36:
            AvroModel()

    # ToDo (tribunsky.kir): change Type[AvroModel] to more general alais + check derivation from python built-ins
    def add(self, topic: TopicName, value: Type[AvroModel], key: Optional[Type[AvroModel]]) -> None:
        self._values[topic] = ValueSchemaDescription(text=derive(value, topic))
        if key is not None:
            self._keys[topic] = KeySchemaDescription(text=derive(key, topic, is_key=True))
