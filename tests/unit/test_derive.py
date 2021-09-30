import sys
import json
from typing import Optional
from dataclasses import dataclass

import pytest

from wunderkafka.compat.types import AvroModel
from wunderkafka.serdes.avromodel import derive


@dataclass
class SomeData(AvroModel):
    field1: int
    field2: str


@dataclass
class SomeDefaultData(AvroModel):
    field1: Optional[int] = None
    field2: Optional[str] = None


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires >= Python3.7")
def test_dataclass() -> None:
    schema = derive(SomeData, topic='test_data_1')
    assert json.loads(schema) == {
        'type': 'record',
        'name': 'test_data_1_value',
        'fields': [
            {
                'name': 'field1',
                'type': 'long',
            },
            {
                'name': 'field2',
                'type': 'string',
            },
        ],
    }


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires >= Python3.7")
def test_dataclass_defaults() -> None:
    schema = derive(SomeDefaultData, topic='test_data_2')

    assert json.loads(schema) == {
        'type': 'record',
        'name': 'test_data_2_value',
        'fields': [
            {
                'name': 'field1',
                'type': ['null', 'long'],
                'default': None,
            },
            {
                'name': 'field2',
                'type': ['null', 'string'],
                'default': None,
            },
        ],
    }
