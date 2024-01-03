import json
from pathlib import Path
from typing import List, Optional

import pytest
from dataclasses_avroschema.pydantic import AvroBaseModel
from pydantic import BaseModel, UUID4, ValidationError
from pydantic_settings import BaseSettings

from wunderkafka.serdes.avromodel import derive


class AvroNestedClass(AvroBaseModel):
    id: UUID4


class AcroResultClass(AvroBaseModel):
    id: UUID4
    nested: List[AvroNestedClass]


def test_avro_base_model() -> None:
    schema = derive(AcroResultClass, topic='test_data_1')
    assert json.loads(schema) == {
        'type': 'record',
        'name': 'test_data_1_value',
        'fields': [
            {
                'name': 'id',
                'type': {
                    'type': 'string',
                    'logicalType': 'uuid',
                    'pydantic-class': 'UUID4'
                }
            },
            {
                'name': 'nested',
                'type': {
                    'type': 'array',
                    'items': {
                        'type': 'record',
                        'name': 'AvroNestedClass',
                        'fields': [
                            {
                                'name': 'id',
                                'type': {
                                    'type': 'string',
                                    'logicalType': 'uuid',
                                    'pydantic-class': 'UUID4'
                                }
                            }
                        ]
                    },
                    'name': 'nested'
                }
            }
        ]
    }


class NestedModel(BaseModel):
    id: UUID4


def test_simple_base_model() -> None:
    schema = derive(NestedModel, topic='test_data_1')
    assert json.loads(schema) == {
        'type': 'record',
        'name': 'test_data_1_value',
        'fields': [
            {
                'name': 'id',
                'type': {
                    'type': 'string',
                    'logicalType': 'uuid',
                    # FixMe (k.tribunskii): remove this
                    'pydantic-class': 'UUID4'
                }
            }
        ]
    }


class ResultModel(BaseModel):
    id: UUID4
    nested: List[NestedModel]


def test_nested_base_model_list() -> None:
    schema = derive(ResultModel, topic='test_data_1')
    assert json.loads(schema) == {
        'type': 'record',
        'name': 'test_data_1_value',
        'fields': [
            {
                'name': 'id',
                'type': {
                    'type': 'string',
                    'logicalType': 'uuid',
                    # FixMe (k.tribunskii): remove this
                    'pydantic-class': 'UUID4'
                }
            },
            {
                'name': 'nested',
                'type': {
                    'type': 'array',
                    'items': {
                        'type': 'record',
                        'name': 'NestedModel',
                        'fields': [
                            {
                                'name': 'id',
                                'type': {
                                    'type': 'string',
                                    'logicalType': 'uuid',
                                    # FixMe (k.tribunskii): remove this
                                    'pydantic-class': 'UUID4'
                                }
                            }
                        ]
                    },
                    'name': 'nested'
                }
            }
        ]
    }


class HasDictStrSchema(BaseModel):
    dct: dict[str, NestedModel]


def test_nested_base_model_dict_str_key() -> None:
    schema = derive(HasDictStrSchema, topic='test_data_1')
    assert json.loads(schema) == {
        'type': 'record',
        'name': 'test_data_1_value',
        'fields': [
            {
                'name': 'dct',
                'type': {
                    'type': 'map',
                    'values': {
                        'type': 'record',
                        'name': 'NestedModel',
                        'fields': [
                            {
                                'name': 'id',
                                'type': {
                                    'type': 'string',
                                    'logicalType': 'uuid',
                                    'pydantic-class': 'UUID4'
                                }
                            }
                        ]
                    },
                    'name': 'dct'
                }
            }
        ]
    }


class HasDictIntSchema(BaseModel):
    dct: dict[int, NestedModel]


def test_nested_base_model_dict_int_key() -> None:
    # InvalidMap derived from Exception =/
    with pytest.raises(Exception):
        derive(HasDictIntSchema, topic='test_data_1')



class Error(BaseModel):
    message: str


class ImageNestedModel(BaseModel):
    id: UUID4
    nested: Optional[NestedModel]
    error: Optional[Error]


def test_nested_base_model_optional() -> None:
    schema = derive(ImageNestedModel, topic='test_data_1')
    assert json.loads(schema) == {
        'type': 'record',
        'name': 'test_data_1_value',
        'fields': [
            {
                'name': 'id',
                'type': {
                    'type': 'string',
                    'logicalType': 'uuid',
                    'pydantic-class': 'UUID4'
                }
            },
            {
                'name': 'nested',
                'type': [
                    {
                        'type': 'record',
                        'name': 'NestedModel',
                        'fields': [
                            {
                                'name': 'id',
                                'type': {
                                    'type': 'string',
                                    'logicalType': 'uuid',
                                    'pydantic-class': 'UUID4'
                                }
                            }
                        ]
                    },
                    'null'
                ]
            },
            {
                'name': 'error',
                'type': [
                    {
                        'type': 'record',
                        'name': 'Error',
                        'fields': [
                            {
                                'name': 'message',
                                'type': 'string'
                            }
                        ]
                    },
                    'null'
                ]
            }
        ]
    }


class DeepNestedModel(BaseModel):
    result: ResultModel


def test_deep_nested_base_model() -> None:
    schema = derive(DeepNestedModel, topic='test_data_1')
    assert json.loads(schema) == {
        'type': 'record',
        'name': 'test_data_1_value',
        'fields': [
            {
                'name': 'result',
                'type': {
                    'type': 'record',
                    'name': 'ResultModel',
                    'fields': [
                        {
                            'name': 'id',
                            'type': {
                                'type': 'string',
                                'logicalType': 'uuid',
                                'pydantic-class': 'UUID4'
                            }
                        },
                        {
                            'name': 'nested',
                            'type': {
                                'type': 'array',
                                'items': {
                                    'type': 'record',
                                    'name': 'NestedModel',
                                    'fields': [
                                        {
                                            'name': 'id',
                                            'type': {
                                                'type': 'string',
                                                'logicalType': 'uuid',
                                                'pydantic-class': 'UUID4'
                                            }
                                        }
                                    ]
                                },
                                'name': 'nested'
                            }
                        }
                    ]
                }
            }
        ]
    }


class MLConfig(BaseSettings):
    weights: Path
    threshold: float = 0.5


class MetricV22(BaseSettings):
    line_speed: Optional[int]
    defect_detected: Optional[bool] = False
    model_on: Optional[bool] = False
    squad_number: int = 0
    model_config: MLConfig                                                               # type: ignore[assignment,misc]

    class Config:
        extra = 'allow'


def test_pydantic_base_settings_v22_with_defaults_complicated_field() -> None:
    with pytest.raises(ValueError):
        derive(MetricV22, topic='some_topic')

    with pytest.raises(ValidationError):
        MetricV22(line_speed=2, model_config=MLConfig(path='test'))  # type: ignore
