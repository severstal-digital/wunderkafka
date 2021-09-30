"""This module contains custom exceptions for the package."""

from confluent_kafka import KafkaException


class ConsumerException(KafkaException):
    """Break control flow if there are any problems with consumer."""


class SerDesException(RuntimeError):
    """Break control flow if there are any problems with (de)serialization."""


class SerializerException(SerDesException):
    """Break control flow if there are any problems with serialization."""


class DeserializerException(SerDesException):
    """Break control flow if there are any problems with deserialization."""


class SchemaRegistryLookupException(RuntimeError):
    """Break control flow if there are any problems with schema id handling.."""
