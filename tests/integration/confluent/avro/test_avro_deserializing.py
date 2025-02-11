from typing import List
from pathlib import Path

import pytest

from tests.integration.confluent.conftest import Msg
from wunderkafka.consumers.types import StreamResult
from wunderkafka.serdes.headers import ConfluentClouderaHeadersHandler
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
    consumer = HighLevelDeserializingConsumer(
        consumer=TestConsumer([Message(topic, value=SIGNAL_MESSAGE.serialized(header))]),
        schema_registry=ConfluentSRClient(TestHTTPClient(sr_root_existing), SimpleCache()),
        headers_handler=ConfluentClouderaHeadersHandler().parse,
        deserializer=FastAvroDeserializer(),
        stream_result=True,
    )

    consumer.subscribe([topic], from_beginning=True)

    events: list[StreamResult] = consumer.consume()
    [event] = events

    assert event.payload == SIGNAL_MESSAGE.deserialized
