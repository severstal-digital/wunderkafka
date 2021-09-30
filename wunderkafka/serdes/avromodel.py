import json
from typing import Type
from dataclasses import is_dataclass

from wunderkafka.compat.types import AvroModel


def derive(model: Type[AvroModel], topic: str, *, is_key: bool = False) -> str:
    if is_dataclass(model):
        model_schema = model.avro_schema_to_python()
    else:
        fixed_model = _get_non_dataclass_model(model)
        model_schema = fixed_model.avro_schema_to_python()
    model_schema.pop('doc')
    suffix = 'key' if is_key else 'value'
    if hasattr(model, 'Meta') and hasattr(model.Meta, 'name'):
        model_schema['name'] = model.Meta.name
    else:
        model_schema['name'] = '{0}_{1}'.format(topic, suffix)
    return json.dumps(model_schema)


def _get_non_dataclass_model(type_: Type[AvroModel]) -> AvroModel:
    fields = vars(type_)['__annotations__']
    for base in type_.mro():
        fields = {**vars(base).get('__annotations__', {}), **fields}

    for field in ['__slots__', 'klass', 'metadata', 'schema_def']:
        fields.pop(field, None)
    return type(type_.__name__, (AvroModel,), {**dict(vars(type_)), '__annotations__': fields})
