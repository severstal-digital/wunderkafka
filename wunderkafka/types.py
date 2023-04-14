"""This module contains aliases and helper definitions for type hints."""

# ToDo (tribunsky.kir): move it to module with structures
from typing import Any, Tuple, Union, Callable, Optional, Type, List

from confluent_kafka import Message, KafkaError, Consumer, TopicPartition

from wunderkafka.structures import Offset, SRMeta, Timestamp, ParsedHeader, SchemaDescription

# ToDo (tribunsky.kir): add symmetry and generalize this part
HeaderParser = Callable[[bytes], ParsedHeader]
HeaderPacker = Callable[[int, SRMeta], bytes]

AssignCallback = Callable[[Consumer, List[TopicPartition]], Any]
DeliveryCallback = Callable[[Optional[KafkaError], Message], None]

MsgValue = Any
MsgKey = Any

KeySchemaDescription = SchemaDescription
ValueSchemaDescription = SchemaDescription

MessageDescription = Union[str, Tuple[str, str], Type, Tuple[Type, Type]]
TopicName = str

HowToSubscribe = Optional[Union[Timestamp, Offset]]
