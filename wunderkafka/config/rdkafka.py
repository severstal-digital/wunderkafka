import os
from collections.abc import Mapping
from enum import Enum
from types import MappingProxyType
from typing import Any, Optional, TypeVar, Union

from wunderkafka.config.generated.fields import COMMON_FIELDS, CONSUMER_FIELDS, PRODUCER_FIELDS
from wunderkafka.config.generated.models import RDConsumerConfig, RDProducerConfig
from wunderkafka.config.schema_registry import SRConfig
from wunderkafka.logger import logger

CONF_CONSUMER_FIELDS = MappingProxyType({
    field_name.replace('.', '_'): field_name for field_name in (*COMMON_FIELDS, *CONSUMER_FIELDS)
})

CONF_PRODUCER_FIELDS = MappingProxyType({
    field_name.replace('.', '_'): field_name for field_name in (*COMMON_FIELDS, *PRODUCER_FIELDS)
})

ConfigValues = Union[str, int, bool, float]


def remap_properties(
    dct: dict[str, Optional[ConfigValues]],
    mapping: Mapping[str, str],
) -> dict[str, ConfigValues]:
    new_dct = {}
    for f_name, f_value in dct.items():
        if f_value is not None:
            to_add = f_value
            if isinstance(f_value, Enum):
                to_add = f_value.value
            new_dct[mapping[f_name]] = to_add
    return new_dct


# ToDo (tribunsky.kir): I need separate common place to do somthing with config before feeding it to librdkafka
#                       or write more complex generator and class hierarchy (e.g. platform-specific base classes)
#                       to not monkeypatch config before actually feeding it to librdkafka.
#                       #TypeSafety!!1
def sanitize(dct: dict[str, ConfigValues]) -> dict[str, ConfigValues]:
    # cimpl.KafkaException: KafkaError{
    #   ...
    #   "Configuration property "ssl.ca.certificate.stores" not supported in this build: configuration only valid on Windows"  # noqa: E501
    #  }
    if os.name != 'nt':
        property_name = 'ssl.ca.certificate.stores'
        property_value = dct.pop(property_name, None)
        if property_value is not None:
            logger.warning('Excluding {}={} as windows-only even it was set to default'.format(
                property_name, property_value,
            ))
    return dct


# I don't like mixing SR config and librdkafka config,
# but it's more handful for producer w/o schema (no need to nest config for librdkafka)
class ConsumerConfig(RDConsumerConfig):
    # https://docs.pydantic.dev/latest/migration/#required-optional-and-nullable-fields
    sr: Optional[SRConfig] = None

    def dict(self, **kwargs: Any) -> dict[str, ConfigValues]:
        dct = super().model_dump(**kwargs)
        dct.pop('sr')
        return sanitize(remap_properties(dct, CONF_CONSUMER_FIELDS))


class ProducerConfig(RDProducerConfig):
    # https://docs.pydantic.dev/latest/migration/#required-optional-and-nullable-fields
    sr: Optional[SRConfig] = None

    def dict(self, **kwargs: Any) -> dict[str, ConfigValues]:
        dct = super().model_dump(**kwargs)
        dct.pop('sr')
        return sanitize(remap_properties(dct, CONF_PRODUCER_FIELDS))


RDKafkaConfig = TypeVar('RDKafkaConfig', ConsumerConfig, ProducerConfig)
