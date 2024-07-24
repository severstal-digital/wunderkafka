from typing import Any, Dict, List
from pathlib import Path
from dataclasses import dataclass

import pytest

from wunderkafka.serdes.headers import ConfluentClouderaHeadersHandler
from wunderkafka.tests import TestConsumer, TestHTTPClient
from wunderkafka.serdes.avro import FastAvroDeserializer
from wunderkafka.tests.consumer import Message
from wunderkafka.schema_registry import SimpleCache, ClouderaSRClient
from wunderkafka.consumers.constructor import HighLevelDeserializingConsumer


@dataclass
class Msg(object):
    payload: bytes
    deserialized: Dict[str, Any]

    def serialized(self, header: bytes) -> bytes:
        return header + self.payload


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
    b'\x01\x00\x00\x00\x00\x00\x00\x06\x9c\x00\x00\x00\x01',
    b'\x02\x00\x00\x00\x00\x00\x00\x08<',
    b'\x03\x00\x00\x08<',
)


@pytest.mark.parametrize("header", list(HEADERS))
def test_consume_moving_parts(sr_root: Path, topic: str, header: bytes) -> None:
    consumer = HighLevelDeserializingConsumer(
        consumer=TestConsumer([Message(topic, value=SIGNAL_MESSAGE.serialized(header))]),
        schema_registry=ClouderaSRClient(TestHTTPClient(sr_root), SimpleCache()),
        headers_handler=ConfluentClouderaHeadersHandler().parse,
        deserializer=FastAvroDeserializer(),
    )

    consumer.subscribe([topic], from_beginning=True)

    msgs: List[Message] = consumer.consume()
    [message] = msgs
    assert message.key() is None
    assert message.value() == SIGNAL_MESSAGE.deserialized
