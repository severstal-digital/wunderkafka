"""This module contains aliases and helper definitions for type hints."""

# ToDo (tribunsky.kir): move it to module with structures
from typing import Any, Tuple, Union, Callable, Optional, Type

from confluent_kafka import Message, KafkaError

from wunderkafka.structures import Offset, SRMeta, Timestamp, ParsedHeader, SchemaDescription

# ToDo (tribunsky.kir): add symmetry and generalize this part
HeaderParser = Callable[[bytes], ParsedHeader]
HeaderPacker = Callable[[int, SRMeta], bytes]

DeliveryCallback = Callable[[Optional[KafkaError], Message], None]

MsgValue = Any
MsgKey = Any

KeySchemaDescription = SchemaDescription
ValueSchemaDescription = SchemaDescription

MessageDescription = Union[str, Tuple[str, str], Type, Tuple[Type, Type]]
TopicName = str

HowToSubscribe = Optional[Union[Timestamp, Offset]]
