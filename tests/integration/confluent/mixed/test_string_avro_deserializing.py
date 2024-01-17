from typing import List
from pathlib import Path

import pytest

from tests.integration.confluent.conftest import Msg
from wunderkafka.serdes.headers import ConfluentClouderaHeadersHandler
from wunderkafka.serdes.string.deserializers import StringDeserializer
from wunderkafka.tests import TestConsumer, TestHTTPClient
from wunderkafka.serdes.avro import FastAvroDeserializer
from wunderkafka.tests.consumer import Message
from wunderkafka.schema_registry import SimpleCache, ConfluentSRClient
from wunderkafka.consumers.constructor import HighLevelDeserializingConsumer


SIGNAL_MESSAGE = Msg(
    payload=b'\x08test\x0cstring\x0cstring\x04NA\xcc\xb8\xeb\xa6\x80_',
    deserialized={
        'source': 'test',
        'type': 'string',
        'id': 'string',
        'value': 'NA',
        'ts': 1632128298534,
    },
)


HEADERS = (
    b'\x00\x00\x00\x08<',
)


@pytest.mark.parametrize("header", list(HEADERS))
def test_consume_moving_parts(sr_root_existing: Path, topic: str, header: bytes) -> None:
    msg = Message(topic, value=SIGNAL_MESSAGE.serialized(header), key=b'1632128298534')
    consumer = HighLevelDeserializingConsumer(
        consumer=TestConsumer([msg]),
        schema_registry=ConfluentSRClient(TestHTTPClient(sr_root_existing), SimpleCache()),
        headers_handler=ConfluentClouderaHeadersHandler().parse,
        value_deserializer=FastAvroDeserializer(),
        key_deserializer=StringDeserializer(),
    )

    consumer.subscribe([topic], from_beginning=True)

    messages: List[Message] = consumer.consume()
    [message] = messages
    assert message.key() == '1632128298534'
    assert message.value() == SIGNAL_MESSAGE.deserialized
