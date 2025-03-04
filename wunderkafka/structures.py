"""This module contains common datastructures which is used in the package."""
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from wunderkafka.time import ts2dt


class SchemaType(str, Enum):
    AVRO = 'AVRO'
    JSON = 'JSON'
    PROTOBUF = 'PROTOBUF'
    # Strings, doubles, integers
    PRIMITIVES = 'PRIMITIVES'


@dataclass(frozen=True)
class Timestamp:
    value: int

    def __str__(self) -> str:
        return f'{self.__class__.__name__}: {self.value:.2f} ({ts2dt(self.value)})'


@dataclass(frozen=True)
class Offset:
    value: int


# ToDo (ka.tribunskii): compose header & meta in symmetrical way
@dataclass(frozen=True)
class ParsedHeader:
    protocol_id: int
    meta_id: Optional[int]
    schema_id: Optional[int]
    schema_version: Optional[int]
    size: int


@dataclass(frozen=True)
class SchemaMeta:
    topic: str
    is_key: bool
    header: ParsedHeader

    @property
    def subject(self) -> str:
        """
        Return topic mapped to schema registry entity.

        :return:            String which should be used as a path in schema registry's url
                            corresponding to a given topic.
        """
        # Confluent
        if self.header.protocol_id == 0:
            suffix = '_key' if self.is_key else '_value'
        # Cloudera
        else:
            suffix = ':k' if self.is_key else ''
        return f'{self.topic}{suffix}'


# ToDo: (tribunsky.kir): add cross-validation of invariants on the model itself?
@dataclass(frozen=True)
class SRMeta:
    """Meta, which is retrieved after schema registration."""
    # Confluent always has schema_id, but one of cloudera protocols doesn't use it
    schema_id: Optional[int]
    # Confluent has schema_version, but serdes works around schema_id, which is a unique identifier there.
    schema_version: Optional[int]
    # Confluent doesn't have metaId
    meta_id: Optional[int] = None


@dataclass(frozen=True)
class SerializerSchemaDescription:
    """
    Class to allow a contract extension between moving parts of serialization.

    Usually schema is represented by text, but separate class adds abstraction.
    """

    text: str

    @property
    def empty(self) -> bool:
        """
        Return True if schema is empty.

        Some serializers (e.g., confluent StringSerializer) practically don't have an effective schema.
        """
        return self.text == ''


@dataclass(frozen=True)
class DeserializerSchemaDescription(SerializerSchemaDescription):
    """
    Class to allow a contract extension between moving parts of deserialization.

    Usually schema is represented by text, but separate class adds abstraction.
    """

    text: str
    type: SchemaType
