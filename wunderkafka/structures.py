"""This module contains common datastructures which is used in the package."""

from typing import Optional
from dataclasses import dataclass

from wunderkafka.time import ts2dt


@dataclass(frozen=True)
class Timestamp(object):
    value: float

    def __str__(self) -> str:
        return '{0}: {1:.2f} ({2})'.format(self.__class__.__name__, self.value, ts2dt(self.value))


@dataclass(frozen=True)
class Offset(object):
    value: int


# ToDo (ka.tribunskii): compose header & meta in symmetrical way
@dataclass(frozen=True)
class ParsedHeader(object):
    protocol_id: int
    meta_id: Optional[int]
    schema_id: Optional[int]
    schema_version: Optional[int]
    size: int


@dataclass(frozen=True)
class SchemaMeta(object):
    topic: str
    is_key: bool
    header: ParsedHeader

    @property
    def subject(self) -> str:
        """
        Return topic mapped to schema registry entity.

        :return:            String which should be used as path in schema registry's url corresponding to a given topic.
        """
        # Confluent
        if self.header.protocol_id == 0:
            suffix = '-key' if self.is_key else '-value'
        # Cloudera
        else:
            suffix = ':k' if self.is_key else ''
        return '{0}{1}'.format(self.topic, suffix)


@dataclass(frozen=True)
class SRMeta(object):
    """Meta which is retrieved after schema registration."""
    schema_id: int
    schema_version: int
    # Confluent doesn't have metaId
    meta_id: Optional[int] = None


@dataclass(frozen=True)
class SchemaDescription(object):
    """
    Class to allow extend contract between moving parts of (de)serialization.

    Usually schema is represented by text, but separate class adds abstraction.
    """

    text: str
