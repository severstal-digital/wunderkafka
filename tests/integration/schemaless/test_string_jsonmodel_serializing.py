import uuid
from typing import Optional
from uuid import UUID

import pytest
from pydantic import BaseModel

from wunderkafka.serdes.json import HAS_JSON_SCHEMA
from wunderkafka.serdes.schemaless.jsonmodel.serializers import SchemaLessJSONModelSerializer
from wunderkafka.serdes.schemaless.string.serializers import StringSerializer

if not HAS_JSON_SCHEMA:
    pytest.skip("skipping json-schema-only tests", allow_module_level=True)


from wunderkafka.producers.constructor import HighLevelSerializingProducer
from wunderkafka.tests import TestProducer


class Image(BaseModel):
    id: Optional[UUID] = None
    path: Optional[str] = None


def test_json_producer_string_key_create_schema() -> None:
    topic = "testing_json_str_producer"
    test_producer = TestProducer()
    producer = HighLevelSerializingProducer(
        producer=test_producer,
        schema_registry=None,
        header_packer=None,
        value_serializer=SchemaLessJSONModelSerializer(),
        key_serializer=StringSerializer(),
        mapping={topic: (Image, str)},
        protocol_id=0,
    )

    key = "714fc713-37ff-4477-9157-cb4f14b63e1a"
    value = Image(
        id=uuid.UUID(key),
        path="/var/folders/x5/zlpmj3915pqfj5lhnlq5qwkm0000gn/T/tmprq2rktq3",
    )

    producer.send_message(topic, value, key)

    [message] = test_producer.sent

    assert message.key == b'714fc713-37ff-4477-9157-cb4f14b63e1a'
    assert message.value == b'{"id":"714fc713-37ff-4477-9157-cb4f14b63e1a","path":"/var/folders/x5/zlpmj3915pqfj5lhnlq5qwkm0000gn/T/tmprq2rktq3"}'  # noqa: E501
