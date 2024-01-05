from typing import Type, Union, Optional
from pathlib import Path

from pydantic import BaseModel
from pydantic.json_schema import GenerateJsonSchema

from wunderkafka.serdes.jsonmodel.derive import JSONClosedModelGenerator
from wunderkafka.types import TopicName, KeySchemaDescription, ValueSchemaDescription
from wunderkafka.serdes.abc import AbstractDescriptionStore
from dataclasses_avroschema import AvroModel
from wunderkafka.serdes import avromodel
from wunderkafka.serdes import jsonmodel


class SchemaTextRepo(AbstractDescriptionStore):

    def add(self, topic: TopicName, value: str, key: str) -> None:
        self._values[topic] = ValueSchemaDescription(text=value)
        if key is not None:
            self._keys[topic] = KeySchemaDescription(text=key)


def _load_from_file(filename: Path) -> str:
    with open(filename) as fl:
        return fl.read()


# ToDo (tribunsky.kir): refactor it, maybe add hooks to parent class.
#                       Barbara, forgive us. Looks like AbstractDescriptionStore should be generic.
class SchemaFSRepo(AbstractDescriptionStore):

    def add(self, topic: TopicName, value: Union[str, Path], key: Union[str, Path]) -> None:
        self._values[topic] = ValueSchemaDescription(text=_load_from_file(Path(value)))
        if key is not None:
            self._keys[topic] = KeySchemaDescription(text=_load_from_file(Path(key)))


class AvroModelRepo(AbstractDescriptionStore):

    # ToDo (tribunsky.kir): change Type[AvroModel] to more general alias + check derivation from python built-ins
    def add(self, topic: TopicName, value: Type[AvroModel], key: Optional[Type[AvroModel]]) -> None:
        self._values[topic] = ValueSchemaDescription(text=avromodel.derive(value, topic))
        if key is not None:
            self._keys[topic] = KeySchemaDescription(text=avromodel.derive(key, topic, is_key=True))


class JSONRepo(AbstractDescriptionStore):

    def add(self, topic: TopicName, value: str, key: Optional[str]) -> None:
        self._values[topic] = ValueSchemaDescription(text=value)
        if key is not None:
            self._keys[topic] = KeySchemaDescription(text=key)


class JSONModelRepo(AbstractDescriptionStore):
    def __init__(self, schema_generator: Type[GenerateJsonSchema] = JSONClosedModelGenerator) -> None:
        super().__init__()
        self._schema_generator = schema_generator

    def add(self, topic: TopicName, value: Type[BaseModel], key: Optional[Type[BaseModel]]) -> None:
        self._values[topic] = ValueSchemaDescription(text=jsonmodel.derive(value, self._schema_generator))
        if key is not None:
            self._keys[topic] = KeySchemaDescription(text=jsonmodel.derive(key, self._schema_generator))
