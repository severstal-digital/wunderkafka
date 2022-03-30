from typing import Type, Union, Optional
from pathlib import Path

from wunderkafka.types import TopicName, KeySchemaDescription, ValueSchemaDescription
from wunderkafka.serdes.abc import AbstractDescriptionStore
from wunderkafka.compat.types import AvroModel
from wunderkafka.compat.constants import PY36
from wunderkafka.serdes.avromodel import derive


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

    def __init__(self) -> None:
        super().__init__()
        if PY36:
            AvroModel()

    # ToDo (tribunsky.kir): change Type[AvroModel] to more general alias + check derivation from python built-ins
    def add(self, topic: TopicName, value: Type[AvroModel], key: Optional[Type[AvroModel]]) -> None:
        self._values[topic] = ValueSchemaDescription(text=derive(value, topic))
        if key is not None:
            self._keys[topic] = KeySchemaDescription(text=derive(key, topic, is_key=True))
