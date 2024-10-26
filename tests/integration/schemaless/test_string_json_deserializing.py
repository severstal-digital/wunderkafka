from typing import List
from pathlib import Path

import pytest

from wunderkafka.serdes.json import HAS_JSON_SCHEMA
from wunderkafka.serdes.schemaless.json.deserializers import SchemaLessJSONDeserializer
from wunderkafka.serdes.schemaless.string.deserializers import StringDeserializer

if not HAS_JSON_SCHEMA:
    pytest.skip("skipping json-schema-only tests", allow_module_level=True)
from tests.integration.confluent.conftest import Msg


from wunderkafka.tests import TestConsumer
from wunderkafka.tests.consumer import Message
from wunderkafka.consumers.constructor import HighLevelDeserializingConsumer

MESSAGE = Msg(
    payload=b'{"id": "714fc713-37ff-4477-9157-cb4f14b63e1a", "path": "/var/folders/x5/zlpmj3915pqfj5lhnlq5qwkm0000gn/T/tmprq2rktq3"}',
    # noqa: E501
    deserialized={
        "id": "714fc713-37ff-4477-9157-cb4f14b63e1a",
        "path": "/var/folders/x5/zlpmj3915pqfj5lhnlq5qwkm0000gn/T/tmprq2rktq3",
    },
)


def test_consume_moving_parts(topic: str) -> None:
    msg = Message(topic, value=MESSAGE.serialized(b''), key=b'714fc713-37ff-4477-9157-cb4f14b63e1a')
    consumer = HighLevelDeserializingConsumer(
        consumer=TestConsumer([msg]),
        value_deserializer=SchemaLessJSONDeserializer(),
        key_deserializer=StringDeserializer(),
    )

    consumer.subscribe([topic], from_beginning=True)

    messages: List[Message] = consumer.consume()
    [message] = messages
    assert message.key() == '714fc713-37ff-4477-9157-cb4f14b63e1a'
    assert message.value() == MESSAGE.deserialized
