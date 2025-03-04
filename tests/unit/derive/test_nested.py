import json
from typing import Optional
from pathlib import Path

import pytest
from pydantic import UUID4, BaseModel, ValidationError
from pydantic_settings import BaseSettings

from wunderkafka.serdes.avromodel import derive


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
                    'logicalType': 'uuid'
                }
            }
        ]
    }


class ResultModel(BaseModel):
    id: UUID4
    nested: list[NestedModel]


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
                    'logicalType': 'uuid'
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
                                    'logicalType': 'uuid'
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
                                    'logicalType': 'uuid'
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
                    'logicalType': 'uuid'
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
                                    'logicalType': 'uuid'
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
                                'logicalType': 'uuid'
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
                                                'logicalType': 'uuid'
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
