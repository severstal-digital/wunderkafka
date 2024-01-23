import json

from pydantic import BaseModel

from wunderkafka.serdes.avromodel import derive


class MyModel(BaseModel):
    a: int
    b: str


def test_derive_hyphens(topic: str = 'my-topic') -> None:
    schema = derive(MyModel, topic=topic)
    assert json.loads(schema) == {
        'name': 'my_topic_value',
        'type': 'record',
        'fields': [
            {
                'name': 'a',
                'type': 'long'
            },
            {
                'name': 'b',
                'type': 'string'
            },
        ],
    }


def test_derive_leading_underscores(topic: str = '_my-topic') -> None:
    schema = derive(MyModel, topic=topic)
    assert json.loads(schema) == {
        'name': 'my_topic_value',
        'type': 'record',
        'fields': [
            {
                'name': 'a',
                'type': 'long'
            },
            {
                'name': 'b',
                'type': 'string'
            },
        ],
    }
