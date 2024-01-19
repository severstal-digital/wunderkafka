from typing import Optional
from pathlib import Path
from uuid import UUID

import pytest
from pydantic import BaseModel, UUID4

from wunderkafka.serdes.json import HAS_JSON_SCHEMA
from wunderkafka.serdes.store import JSONModelRepo

if not HAS_JSON_SCHEMA:
    pytest.skip("skipping json-schema-only tests", allow_module_level=True)
from wunderkafka.serdes.jsonmodel.serializers import JSONModelSerializer

from wunderkafka.serdes.headers import ConfluentClouderaHeadersHandler
from wunderkafka.tests import TestProducer, TestHTTPClient
from wunderkafka.schema_registry import SimpleCache, ConfluentSRClient
from wunderkafka.producers.constructor import HighLevelSerializingProducer


class Image(BaseModel):
    id: Optional[UUID4] = None
    path: Optional[str] = None


def test_json_producer_create_schema(sr_root_existing: Path) -> None:
    topic = 'testing_json_str_producer'
    test_producer = TestProducer()
    sr_client = ConfluentSRClient(TestHTTPClient(sr_root_existing), SimpleCache())
    producer = HighLevelSerializingProducer(
        producer=test_producer,
        schema_registry=sr_client,
        header_packer=ConfluentClouderaHeadersHandler().pack,
        serializer=JSONModelSerializer(sr_client.client),
        store=JSONModelRepo(),
        mapping={topic: Image},
        protocol_id=0,
    )

    key = None
    value = Image(
        id=UUID("714fc713-37ff-4477-9157-cb4f14b63e1a"),
        path="/var/folders/x5/zlpmj3915pqfj5lhnlq5qwkm0000gn/T/tmprq2rktq3",
    )

    producer.send_message(topic, value, key)

    [message] = test_producer.sent

    assert message.key is None
    assert message.value == b'\x00\x00\x00\x07<{"id": "714fc713-37ff-4477-9157-cb4f14b63e1a", "path": "/var/folders/x5/zlpmj3915pqfj5lhnlq5qwkm0000gn/T/tmprq2rktq3"}'  # noqa: E501
