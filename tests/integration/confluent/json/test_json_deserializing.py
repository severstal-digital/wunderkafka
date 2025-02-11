from typing import List, Optional
from pathlib import Path

import pytest
from pydantic import BaseModel, UUID4

from wunderkafka.serdes.json import HAS_JSON_SCHEMA

if not HAS_JSON_SCHEMA:
    pytest.skip("skipping json-schema-only tests", allow_module_level=True)
from wunderkafka.serdes.json.deserializers import JSONDeserializer

from tests.integration.confluent.conftest import Msg
from wunderkafka.serdes.headers import ConfluentClouderaHeadersHandler
from wunderkafka.tests import TestConsumer, TestHTTPClient
from wunderkafka.tests.consumer import Message
from wunderkafka.schema_registry import SimpleCache, ConfluentSRClient
from wunderkafka.consumers.constructor import HighLevelDeserializingConsumer


class Image(BaseModel):
    id: Optional[UUID4] = None
    path: Optional[str] = None


IMAGE_MESSAGE = Msg(
    payload=b'{"id": "714fc713-37ff-4477-9157-cb4f14b63e1a", "path": "/var/folders/x5/zlpmj3915pqfj5lhnlq5qwkm0000gn/T/tmprq2rktq3"}',  # noqa: E501
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
    consumer = HighLevelDeserializingConsumer(
        consumer=TestConsumer([Message(topic, value=IMAGE_MESSAGE.serialized(header))]),
        schema_registry=ConfluentSRClient(TestHTTPClient(sr_root_existing), SimpleCache()),
        headers_handler=ConfluentClouderaHeadersHandler().parse,
        deserializer=JSONDeserializer(),
    )

    consumer.subscribe([topic], from_beginning=True)

    messages: list[Message] = consumer.consume()
    [message] = messages

    assert message.value() == IMAGE_MESSAGE.deserialized
