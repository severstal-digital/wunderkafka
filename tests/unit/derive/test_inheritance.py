import sys
import json
from typing import Optional

from pydantic import Field, BaseModel

from wunderkafka.serdes.avromodel import derive

if sys.version_info <= (3, 10):
    class ParentOptional(BaseModel):
        volume: float = Field(description='...')
        weight: Optional[float] = Field(description='...')

    class ChildOptional(ParentOptional):
        ts: int = Field(description='...')

    class GrandsonOptional(ChildOptional):
        ...


    def test_dataclass() -> None:
        schema = derive(GrandsonOptional, topic='test_data_1')
        assert json.loads(schema) == {
            'type': 'record',
            'name': 'test_data_1_value',
            'fields': [
                {
                    'name': 'volume',
                    'type': 'double',
                },
                {
                    'name': 'weight',
                    'type': ['double', 'null'],
                },
                {
                    'name': 'ts',
                    'type': 'long',
                },
            ],
        }

else:
    class Parent(BaseModel):
        volume: float = Field(description='...')
        weight: float | None = Field(description='...')


    class Child(Parent):
        ts: int = Field(description='...')


    class Grandson(Child):
        ...

    def test_dataclass_pipe_annotation() -> None:
        schema = derive(Grandson, topic='test_data_1')
        assert json.loads(schema) == {
            'type': 'record',
            'name': 'test_data_1_value',
            'fields': [
                {
                    'name': 'volume',
                    'type': 'double',
                },
                {
                    'name': 'weight',
                    'type': ['double', 'null'],
                },
                {
                    'name': 'ts',
                    'type': 'long',
                },
            ],
        }
