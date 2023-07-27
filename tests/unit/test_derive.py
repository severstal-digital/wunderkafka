import json
import time
from typing import Optional
from datetime import datetime
from dataclasses import dataclass

from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings

from dataclasses_avroschema import AvroModel
from wunderkafka.serdes.avromodel import derive


@dataclass
class SomeData(AvroModel):
    field1: int
    field2: str


@dataclass
class SomeDefaultData(AvroModel):
    field1: Optional[int] = None
    field2: Optional[str] = None


class Metrics(BaseModel):
    line_speed: Optional[int]
    defect_detected: Optional[bool] = False
    model_on: Optional[bool] = False
    squad_number: int = 0


class Metric(BaseSettings):
    line_speed: Optional[int]
    defect_detected: Optional[bool] = False
    model_on: Optional[bool] = False
    squad_number: int = 0


class Event(BaseModel):
    id: Optional[int]
    ts: Optional[int] = None

    class Meta:
        namespace = "any.data"


class Mixed(BaseModel):
    text: str
    value: float
    integer: int = 0
    string: str = 'str'


# Pydantic allows following of non-default arguments, but dataclasses are not.
class ImageData(BaseModel):
    name: str = 'str'
    image: bytes
    camera: str
    ts: float = Field(default_factory=time.time)


class OtherImageData(BaseModel):
    image: bytes
    camera: str
    ts: float = Field(default_factory=time.time)
    name: str = 'str'


class TsWithMeta(BaseModel):
    ts: datetime = Field(default_factory=datetime.now)

    class Meta:
        namespace = 'com.namespace.my'
        name = 'MsgKey'


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


def test_pydantic_with_defaults() -> None:
    schema = derive(Metrics, topic='some_topic')

    assert json.loads(schema) == {
      "type": "record",
      "name": "some_topic_value",
      "fields": [
        {
          "name": "line_speed",
          "type": [
            "long",
            "null"
          ]
        },
        {
          "name": "defect_detected",
          "type": [
            "boolean",
            "null"
          ],
          "default": False
        },
        {
          "name": "model_on",
          "type": [
            "boolean",
            "null"
          ],
          "default": False
        },
        {
          "name": "squad_number",
          "type": "long",
          "default": 0,
        }
      ]
    }


def test_pydantic_defaults() -> None:
    schema = derive(Mixed, topic='topic')

    assert json.loads(schema) == {
        'type': 'record',
        'name': 'topic_value',
        'fields': [
            {
                'type': 'string',
                'name': 'text',
            },
            {
                'type': 'double',
                'name': 'value',
            },
            {
                'type': 'long',
                'name': 'integer',
                'default': 0,
            },
            {
                'type': 'string',
                'name': 'string',
                'default': 'str'
            },
        ],
    }


def test_pydantic_defaults_none() -> None:
    schema = derive(Event, topic='topic')

    assert json.loads(schema) == {
        'type': 'record',
        'name': 'topic_value',
        'namespace': 'any.data',
        'fields': [
            {
                'type': ['long', 'null'],
                'name': 'id',
            },
            {
                'type': ['null', 'long'],
                'name': 'ts',
                'default': None,
            },
        ],
    }


def test_pydantic_mixed_defaults() -> None:
    s1 = derive(ImageData, topic='topic')
    s2 = derive(OtherImageData, topic='topic')
    assert json.loads(s1) == {
        'type': 'record',
        'name': 'topic_value',
        'fields': [
            {
                'name': 'name',
                'type': 'string',
                'default': 'str'
            },
            {
                'name': 'image',
                'type': 'bytes',
            },
            {
                'name': 'camera',
                'type': 'string',
            },
            {
                'name': 'ts',
                'type': 'double',
            },
        ],
    }
    assert json.loads(s1) != json.loads(s2)


def test_pydantic_with_meta() -> None:
    schema = derive(TsWithMeta, topic='topic')

    assert json.loads(schema) == {
        'type': 'record',
        'namespace': 'com.namespace.my',
        'name': 'MsgKey',
        'fields': [
            {
                'name': 'ts',
                'type': {
                    'logicalType': 'timestamp-millis',
                    'type': 'long',
                }
            }
        ],
    }


def test_pydantic_base_settings_with_defaults() -> None:
    schema = derive(Metric, topic='some_topic')

    assert json.loads(schema) == {
      "type": "record",
      "name": "some_topic_value",
      "fields": [
        {
          "name": "line_speed",
          "type": [
            "long",
            "null"
          ]
        },
        {
          "name": "defect_detected",
          "type": [
            "boolean",
            "null"
          ],
          "default": False
        },
        {
          "name": "model_on",
          "type": [
            "boolean",
            "null"
          ],
          "default": False
        },
        {
          "name": "squad_number",
          "type": "long",
          "default": 0,
        }
      ]
    }
