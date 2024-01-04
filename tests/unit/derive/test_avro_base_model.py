import json
from typing import List

from dataclasses_avroschema.pydantic import AvroBaseModel
from pydantic import UUID4

from wunderkafka.serdes.avromodel import derive


class AvroNestedClass(AvroBaseModel):
    id: UUID4


class AcroResultClass(AvroBaseModel):
    id: UUID4
    nested: List[AvroNestedClass]


class AvroSimilarImage(AvroBaseModel):
    id: UUID4


def test_avro_model() -> None:
    schema = derive(AvroSimilarImage, topic='test_data_1')
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
                    'logicalType': 'uuid'
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
