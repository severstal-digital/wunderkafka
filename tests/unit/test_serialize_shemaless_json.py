import datetime
import random
import string
import uuid
from uuid import UUID

import pytest
from pydantic import BaseModel, Field

from wunderkafka.serdes.schemaless.json.serializers import SchemaLessJSONSerializer
from wunderkafka.serdes.schemaless.jsonmodel.serializers import SchemaLessJSONModelSerializer


def get_random_string() -> str:
    return ''.join(random.choice(string.printable) for i in range(random.randint(3, 20)))


def get_random_int() -> int:
    return random.randint(-10_000, 10_000)


class RandomName(BaseModel):
    name: str = Field(default_factory=get_random_string)


class MyData(RandomName):
    id: int = Field(default_factory=get_random_int)


class MyUUIDData(RandomName):
    id: UUID = Field(default_factory=uuid.uuid4)


class MyDateTimeData(RandomName):
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


@pytest.fixture(params=[RandomName, MyData, MyUUIDData, MyDateTimeData])
def my_model(request: pytest.FixtureRequest) -> RandomName:
    return request.param()


def test_serialize_schemaless_json(my_model: RandomName) -> None:
    serializer = SchemaLessJSONSerializer()
    serialized = serializer.serialize("", my_model.model_dump())
    assert isinstance(serialized, bytes)


def test_serialize_schemaless_jsonmodel(my_model: RandomName) -> None:
    serializer = SchemaLessJSONModelSerializer()
    serialized = serializer.serialize("", my_model)
    assert isinstance(serialized, bytes)
