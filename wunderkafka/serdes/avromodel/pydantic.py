from typing import Any, Final, Optional, TypeVar, Union, get_args

try:
    from dataclasses_avroschema.avrodantic import AvroBaseModel
except ImportError:
    from dataclasses_avroschema.pydantic import AvroBaseModel

from pydantic import BaseModel, ConfigDict, create_model
from pydantic_settings import BaseSettings

from wunderkafka.serdes.avromodel.typing import is_generic_type
from wunderkafka.serdes.avromodel.typing.compat import create_annotation, get_generic, is_union_type

A = TypeVar('A', bound=Any)

PYDANTIC_PROTECTED_FIELDS: Final[frozenset[str]] = frozenset({
    'model_config',
    'model_fields',
    # even the latest ones are properties, we don't want to shadow them either
    'model_computed_fields',
    'model_extra',
    'model_fields_set',
})


def exclude_pydantic_class(schema: dict[str, Any]) -> dict[str, Any]:
    schema.pop('pydantic-class', None)
    for value in schema.values():
        if isinstance(value, dict):
            exclude_pydantic_class(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    exclude_pydantic_class(item)
    return schema


def derive_from_pydantic(model_type: type[object]) -> Optional[type[AvroBaseModel]]:
    if issubclass(model_type, AvroBaseModel):
        return model_type
    if issubclass(model_type, BaseModel):
        _check_pydantic_service_fields(model_type)
        return _create_model(model_type)
    return None


def replace_type_in_annotation(annotation: Any) -> Any:
    origin = get_generic(annotation)
    args = get_args(annotation)

    if origin is None:
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            return create_model(annotation.__name__, __base__=(annotation, AvroBaseModel))
        else:
            return annotation

    new_args = [replace_type_in_annotation(arg) for arg in args]

    # https://bugs.python.org/issue45418
    if is_union_type(origin):
        origin = Union

    return create_annotation(origin, new_args)


def get_model_attributes(model_type: type[BaseModel]) -> dict[str, Any]:
    attributes: dict[str, Any] = {}
    for field_name, field_info in model_type.model_fields.items():
        # Here we are changing the original model just for schema derivation, so we can override almost everything
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
                    new_annotation = replace_type_in_annotation(annotation_type)
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


def _check_pydantic_service_fields(model_type: type[object]) -> None:
    if issubclass(model_type, BaseModel):
        all_annotations = set()
        for model in model_type.mro():
            # fragile, maybe it's better to check any of the fields
            is_just_a_base_model = model is BaseModel or model is BaseSettings
            if not is_just_a_base_model:
                for field in vars(model).get('__annotations__', {}):
                    is_real_config_dict = field == 'model_config' and model.__annotations__[field] is ConfigDict
                    if not is_real_config_dict:
                        all_annotations.add(field)
        has_protected_fields = all_annotations & PYDANTIC_PROTECTED_FIELDS
        if has_protected_fields:
            msg = ' '.join([
                f'Pydantic model {model_type} has protected fields {has_protected_fields}.',
                'Please use another name for your field.',
                'Even if we may derive a schema with such field(s), it would be impossible to instantiate a model',
            ])
            raise ValueError(msg)


def _create_model(model_type: type[BaseModel]) -> type[AvroBaseModel]:
    attributes = get_model_attributes(model_type)
    crafted_model = create_model(model_type.__name__, __base__=(model_type, AvroBaseModel), **attributes)
    assert issubclass(crafted_model, AvroBaseModel)
    return crafted_model
