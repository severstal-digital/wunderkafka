"""This module contains aliases and helper definitions for type hints."""

# ToDo (tribunsky.kir): move it to module with structures
from typing import Any, Callable, Optional, Union

from confluent_kafka import KafkaError, Message

from wunderkafka.structures import Offset, ParsedHeader, SchemaDescription, SRMeta, Timestamp

from wunderkafka.structures import Offset, SRMeta, Timestamp, ParsedHeader, DeserializerSchemaDescription

# ToDo (tribunsky.kir): add symmetry and generalize this part
HeaderParser = Callable[[bytes], ParsedHeader]
HeaderPacker = Callable[[int, SRMeta], bytes]

DeliveryCallback = Callable[[Optional[KafkaError], Message], None]

MsgValue = Any
MsgKey = Any

KeySchemaDescription = DeserializerSchemaDescription
ValueSchemaDescription = DeserializerSchemaDescription

MessageDescription = Union[str, tuple[str, str], type, tuple[type, type]]
TopicName = str

HowToSubscribe = Optional[Union[Timestamp, Offset]]
