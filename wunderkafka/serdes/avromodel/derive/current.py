import json
import re
from dataclasses import is_dataclass
from typing import Any

from dataclasses_avroschema import AvroModel

from wunderkafka.logger import logger
from wunderkafka.serdes.avromodel.pydantic import derive_from_pydantic, exclude_pydantic_class


def derive(model_type: type[object], topic: str, *, is_key: bool = False) -> str:
    pydantic_model = derive_from_pydantic(model_type)
    if pydantic_model is None:
        if is_dataclass(model_type):
            # https://github.com/python/mypy/issues/14941
            model_schema = model_type.avro_schema_to_python()                                             # type: ignore
        else:
            # Non-dataclasses objects may allow mixing defaults and non-default fields order,
            # so to still reuse dataclasses_avroschema, we extract fields and reorder them to satisfy dataclasses
            # restrictions, than reorder them back.
            # All these hacks will work only for flat schemas:
            #   we avoid describing objects via nested types for HDFS's sake.
            attributes = _extract_attributes(model_type)
            ordering = list(attributes['__annotations__'])
            crafted_model: type[AvroModel] = type(model_type.__name__, (AvroModel,), attributes)
            model_schema = crafted_model.avro_schema_to_python()
            fields_map = {field_data['name']: field_data for field_data in model_schema['fields']}
            reordered_fields = [fields_map[attr] for attr in ordering]
            model_schema['fields'] = reordered_fields
    else:
        model_schema = pydantic_model.avro_schema_to_python()
    model_schema.pop('doc', None)
    suffix = 'key' if is_key else 'value'
    if hasattr(model_type, 'Meta') and hasattr(model_type.Meta, 'name'):
        model_schema['name'] = model_type.Meta.name
    else:
        model_schema['name'] = '{}_{}'.format(re.sub(r'[^\w_]', '_', topic), suffix)
    if model_schema['name'].startswith('_'):
        logger.warning('Topic name {0} starts with underscore, which is not allowed for Avro schema names.')
        model_schema['name'] = model_schema['name'][1:]
    if pydantic_model:
        # I would not prefer to just override PydanticParser because it always may be broken or thrown-out
        model_schema = exclude_pydantic_class(model_schema)
    for field in model_schema.get('fields', []):
        field.pop('doc', None)
    return json.dumps(model_schema)


def _extract_attributes(type_: type[object]) -> dict[str, Any]:
    fields = vars(type_).get('__annotations__', {})
    _, *parents = type_.mro()
    for base in parents:
        new_fields = {**vars(base).get('__annotations__', {})}
        # Currently it is `model_config: ClassVar[SettingsConfigDict]`
        # https://github.com/pydantic/pydantic-settings/blob/919a20b77527ecc1cd6eeb0a09ca22cc21486fb8/pydantic_settings/main.py#L166
        for field in ['__slots__', 'klass', 'metadata', 'schema_def', '__config__', 'model_config']:
            new_fields.pop(field, None)
        fields = {**new_fields, **fields}

    attributes = {}
    attributes.update({'__annotations__': fields})
    meta = vars(type_).get('Meta', None)
    if meta is not None:
        attributes.update({'Meta': meta})
    return attributes
