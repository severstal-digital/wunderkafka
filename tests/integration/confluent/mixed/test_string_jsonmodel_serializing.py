from pathlib import Path
from typing import Optional
from uuid import UUID

import pytest
from pydantic import UUID4, BaseModel

from wunderkafka.serdes.json import HAS_JSON_SCHEMA
from wunderkafka.serdes.schemaless.string.serializers import StringSerializer

if not HAS_JSON_SCHEMA:
    pytest.skip("skipping json-schema-only tests", allow_module_level=True)

from wunderkafka.producers.constructor import HighLevelSerializingProducer
from wunderkafka.schema_registry import ConfluentSRClient, SimpleCache
from wunderkafka.serdes.headers import ConfluentClouderaHeadersHandler
from wunderkafka.serdes.jsonmodel.serializers import JSONModelSerializer
from wunderkafka.tests import TestHTTPClient, TestProducer


class Image(BaseModel):
    id: Optional[UUID4] = None
    path: Optional[str] = None


def test_json_producer_string_key_create_schema(sr_root_existing: Path) -> None:
    topic = "testing_json_str_producer"
    test_producer = TestProducer()
    sr_client = ConfluentSRClient(TestHTTPClient(sr_root_existing), SimpleCache())
    producer = HighLevelSerializingProducer(
        producer=test_producer,
        schema_registry=sr_client,
        header_packer=ConfluentClouderaHeadersHandler().pack,
        value_serializer=JSONModelSerializer(sr_client.client),
        key_serializer=StringSerializer(),
        mapping={topic: (Image, str)},
        protocol_id=0,
    )

    key = "714fc713-37ff-4477-9157-cb4f14b63e1a"
    value = Image(
        id=UUID("714fc713-37ff-4477-9157-cb4f14b63e1a"),
        path="/var/folders/x5/zlpmj3915pqfj5lhnlq5qwkm0000gn/T/tmprq2rktq3",
    )

    producer.send_message(topic, value, key)

    [message] = test_producer.sent

    assert message.key == b'714fc713-37ff-4477-9157-cb4f14b63e1a'
    assert message.value == b'\x00\x00\x00\x07<{"id": "714fc713-37ff-4477-9157-cb4f14b63e1a", "path": "/var/folders/x5/zlpmj3915pqfj5lhnlq5qwkm0000gn/T/tmprq2rktq3"}'  # noqa: E501
