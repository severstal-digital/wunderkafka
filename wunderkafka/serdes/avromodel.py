import json
from typing import Any, Dict, Type
from dataclasses import is_dataclass

from pydantic import BaseModel
from pydantic.fields import ModelField, UndefinedType

from dataclasses_avroschema import AvroModel


def derive(model: Type[object], topic: str, *, is_key: bool = False) -> str:
    if is_dataclass(model):
        # https://github.com/python/mypy/issues/14941
        model_schema = model.avro_schema_to_python()                                                      # type: ignore
    else:
        # non-dataclasses objects may allow mixing defaults and non-default fields order,
        # so to still reuse dataclasses_avroschema, we extract fields and reorder them to satisfy dataclasses
        # restrictions, than reorder them back.
        # All this hacks will work only for flat schemas: we avoid describing objects via nested types for HDFS's sake.
        attributes = _extract_attributes(model)
        ordering = list(attributes['__annotations__'])
        crafted_model = _construct_model(attributes, model)
        model_schema = crafted_model.avro_schema_to_python()
        fields_map = {field_data['name']: field_data for field_data in model_schema['fields']}
        reordered_fields = [fields_map[attr] for attr in ordering]
        model_schema['fields'] = reordered_fields
    model_schema.pop('doc', None)
    suffix = 'key' if is_key else 'value'
    if hasattr(model, 'Meta') and hasattr(model.Meta, 'name'):
        model_schema['name'] = model.Meta.name
    else:
        model_schema['name'] = '{0}_{1}'.format(topic, suffix)
    return json.dumps(model_schema)


def _construct_model(attrs: Dict[str, Any], type_: Type[object]) -> AvroModel:
    if issubclass(type_, BaseModel):
        for field in vars(type_).get('__fields__', {}).values():
            if isinstance(field, ModelField) and not isinstance(field.field_info.default, UndefinedType):
                attrs[field.name] = field.default
                tp = attrs['__annotations__'].pop(field.name)
                attrs['__annotations__'].update({field.name: tp})
    # https://docs.python.org/3/library/functions.html?highlight=type#type
    return type(type_.__name__, (AvroModel,), attrs)                                                      # type: ignore


def _extract_attributes(type_: Type[object]) -> Dict[str, Any]:
    fields = vars(type_).get('__annotations__', {})
    for base in type_.mro():
        fields = {**vars(base).get('__annotations__', {}), **fields}
    for field in ['__slots__', 'klass', 'metadata', 'schema_def', '__config__']:
        fields.pop(field, None)
    attributes = {}
    attributes.update({'__annotations__': fields})
    meta = vars(type_).get('Meta', None)
    if meta is not None:
        attributes.update({'Meta': meta})
    return attributes
