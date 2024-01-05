from pathlib import Path

import pytest


from wunderkafka.serdes.json import HAS_JSON_SCHEMA

if not HAS_JSON_SCHEMA:
    pytest.skip("skipping json-schema-only tests", allow_module_level=True)
from wunderkafka.serdes.store import JSONRepo
from wunderkafka.serdes.json.serializers import JSONSerializer

from wunderkafka.serdes.headers import ConfluentClouderaHeadersHandler
from wunderkafka.tests import TestProducer, TestHTTPClient
from wunderkafka.schema_registry import SimpleCache, ConfluentSRClient
from wunderkafka.producers.constructor import HighLevelSerializingProducer


def test_json_producer_create_schema(sr_root_existing: Path, topic: str) -> None:
    schema_str = '{"properties": {"id": {"anyOf": [{"format": "uuid4", "type": "string"}, {"type": "null"}], "default": null, "title": "Id"}, "path": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null, "title": "Path"}}, "title": "Image", "type": "object", "additionalProperties": false}'
    test_producer = TestProducer()
    sr_client = ConfluentSRClient(TestHTTPClient(sr_root_existing), SimpleCache())
    producer = HighLevelSerializingProducer(
        producer=test_producer,
        schema_registry=sr_client,
        header_packer=ConfluentClouderaHeadersHandler().pack,
        serializer=JSONSerializer(sr_client.client),
        store=JSONRepo(),
        mapping={topic: schema_str},
        protocol_id=0,
    )

    key = None
    value = {
        "id": "714fc713-37ff-4477-9157-cb4f14b63e1a",
        "path": "/var/folders/x5/zlpmj3915pqfj5lhnlq5qwkm0000gn/T/tmprq2rktq3",
    }


    producer.send_message(topic, value, key)

    [message] = test_producer.sent

    assert message.key is None
    assert message.value == b'\x00\x00\x00\x07<{"id": "714fc713-37ff-4477-9157-cb4f14b63e1a", "path": "/var/folders/x5/zlpmj3915pqfj5lhnlq5qwkm0000gn/T/tmprq2rktq3"}'
