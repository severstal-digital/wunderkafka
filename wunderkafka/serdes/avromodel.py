import json
from typing import Any, Dict, Type, Union, get_origin, get_args, FrozenSet, Final, Optional
from dataclasses import is_dataclass

from dataclasses_avroschema import AvroModel
from dataclasses_avroschema.pydantic import AvroBaseModel
from pydantic import BaseModel, create_model, ConfigDict
from pydantic_settings import BaseSettings

from wunderkafka.serdes.compat.typing import get_generic, create_annotation, is_union_type

PYDANTIC_PROTECTED_FIELDS: Final[FrozenSet[str]] = frozenset({
    'model_config',
    'model_fields',
    # even the latest ones are properties, we don't want to shadow them too
    'model_computed_fields',
    'model_extra',
    'model_fields_set',
})


def is_generic_type(annotation: Optional[Type[object]]) -> bool:
    return get_origin(annotation) is not None and len(get_args(annotation)) > 0


def get_model_attributes(model_type: Type[BaseModel]) -> Dict[str, Any]:
    attributes: Dict[str, Any] = {}
    for field_name, field_info in model_type.model_fields.items():
        # Here we are changing original model just for schema derivation, so we can override almost everything
        # https://github.com/marcosschroh/dataclasses-avroschema/issues/400
        if field_info.default_factory is not None:
            field_info.default_factory = None
        annotation_type = field_info.annotation
        if isinstance(annotation_type, BaseModel):
            attributes[field_name] = create_model(model_type.__name__, __base__=(annotation_type, AvroBaseModel))
        else:
            if annotation_type is None:
                attributes[field_name] = (annotation_type, field_info)
            else:
                if is_generic_type(annotation_type):
                    types_list = []
                    for arg in get_args(annotation_type):
                        if issubclass(arg, BaseModel):
                            types_list.append(create_model(arg.__name__, __base__=(arg, AvroBaseModel)))
                        else:
                            types_list.append(arg)
                    generic = get_generic(annotation_type)
                    # already checked in is_generic_type
                    # so this is just for mypy only
                    assert generic is not None
                    # https://bugs.python.org/issue45418
                    union_type = is_union_type(generic)
                    if union_type:
                        generic = Union
                    new_annotation = create_annotation(generic, types_list)
                    field_info.annotation = new_annotation
                    attributes[field_name] = (new_annotation, field_info)
                else:
                    if issubclass(annotation_type, BaseModel):
                        new_type = _create_model(annotation_type)
                        field_info.annotation = new_type
                        attributes[field_name] = (new_type, field_info)
                    else:
                        attributes[field_name] = (annotation_type, field_info)
    return attributes


def _create_model(model_type: Type[BaseModel]) -> Type[AvroBaseModel]:
    attributes = get_model_attributes(model_type)
    crafted_model = create_model(model_type.__name__, __base__=(model_type, AvroBaseModel), **attributes)
    assert issubclass(crafted_model, AvroBaseModel)
    return crafted_model


def _check_pydantic_service_fields(model_type: Type[object]) -> None:
    if issubclass(model_type, BaseModel):
        all_annotations = set()
        for model in model_type.mro():
            # fragile, maybe it's better to check any of the fields
            is_just_a_base_model = model is BaseModel or model is BaseSettings
            if not is_just_a_base_model:
                for annotation in vars(model).get('__annotations__', {}):
                    is_real_config_dict = annotation == 'model_config' and model.__annotations__[annotation] is ConfigDict
                    if not is_real_config_dict:
                        all_annotations.add(annotation)
        has_protected_fields = all_annotations & PYDANTIC_PROTECTED_FIELDS
        if has_protected_fields:
            msg = ' '.join([
                'Pydantic model {0} has protected fields {1}.'.format(model_type, has_protected_fields),
                'Please use another name for your field.',
                'Even if we may derive a schema with such field(s), it would be impossible to instantiate a model',
            ])
            raise ValueError(msg)


def derive(model_type: Type[object], topic: str, *, is_key: bool = False) -> str:
    _check_pydantic_service_fields(model_type)
    if is_dataclass(model_type):
        # https://github.com/python/mypy/issues/14941
        model_schema = model_type.avro_schema_to_python()                                                 # type: ignore
    elif issubclass(model_type, AvroBaseModel):
        model_schema = model_type.avro_schema_to_python()
    elif issubclass(model_type, BaseModel):
        mdl = _create_model(model_type)
        model_schema = mdl.avro_schema_to_python()
    else:
        # non-dataclasses objects may allow mixing defaults and non-default fields order,
        # so to still reuse dataclasses_avroschema, we extract fields and reorder them to satisfy dataclasses
        # restrictions, than reorder them back.
        # All this hacks will work only for flat schemas: we avoid describing objects via nested types for HDFS's sake.
        attributes = _extract_attributes(model_type)
        ordering = list(attributes['__annotations__'])
        crafted_model: AvroModel = type(model_type.__name__, (AvroModel,), attributes)        # type: ignore[assignment]
        model_schema = crafted_model.avro_schema_to_python()
        fields_map = {field_data['name']: field_data for field_data in model_schema['fields']}
        reordered_fields = [fields_map[attr] for attr in ordering]
        model_schema['fields'] = reordered_fields
    model_schema.pop('doc', None)
    suffix = 'key' if is_key else 'value'
    if hasattr(model_type, 'Meta') and hasattr(model_type.Meta, 'name'):
        model_schema['name'] = model_type.Meta.name
    else:
        model_schema['name'] = '{0}_{1}'.format(topic, suffix)
    return json.dumps(model_schema)


def _extract_attributes(type_: Type[object]) -> Dict[str, Any]:
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
