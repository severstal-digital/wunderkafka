from typing import List
from pathlib import Path

import pytest

from wunderkafka.serdes.json import HAS_JSON_SCHEMA

if not HAS_JSON_SCHEMA:
    pytest.skip("skipping json-schema-only tests", allow_module_level=True)
from wunderkafka.tests import TestConsumer, TestHTTPClient
from wunderkafka.serdes.headers import ConfluentClouderaHeadersHandler
from wunderkafka.tests.consumer import Message
from wunderkafka.schema_registry import SimpleCache, ConfluentSRClient
from wunderkafka.consumers.constructor import HighLevelDeserializingConsumer
from tests.integration.confluent.conftest import Msg
from wunderkafka.serdes.json.deserializers import JSONDeserializer
from wunderkafka.serdes.string.deserializers import StringDeserializer

MESSAGE = Msg(
    payload=b'{"id": "714fc713-37ff-4477-9157-cb4f14b63e1a", "path": "/var/folders/x5/zlpmj3915pqfj5lhnlq5qwkm0000gn/T/tmprq2rktq3"}',
    # noqa: E501
    deserialized={
        "id": "714fc713-37ff-4477-9157-cb4f14b63e1a",
        "path": "/var/folders/x5/zlpmj3915pqfj5lhnlq5qwkm0000gn/T/tmprq2rktq3",
    },
)

HEADERS = (
    b'\x00\x00\x00\x07<',
)


@pytest.mark.parametrize("header", list(HEADERS))
def test_consume_moving_parts(sr_root_existing: Path, topic: str, header: bytes) -> None:
    msg = Message(topic, value=MESSAGE.serialized(header), key=b'714fc713-37ff-4477-9157-cb4f14b63e1a')
    consumer = HighLevelDeserializingConsumer(
        consumer=TestConsumer([msg]),
        schema_registry=ConfluentSRClient(TestHTTPClient(sr_root_existing), SimpleCache()),
        headers_handler=ConfluentClouderaHeadersHandler().parse,
        value_deserializer=JSONDeserializer(),
        key_deserializer=StringDeserializer(),
    )

    consumer.subscribe([topic], from_beginning=True)

    messages: List[Message] = consumer.consume()
    [message] = messages
    assert message.key() == '714fc713-37ff-4477-9157-cb4f14b63e1a'
    assert message.value() == MESSAGE.deserialized
