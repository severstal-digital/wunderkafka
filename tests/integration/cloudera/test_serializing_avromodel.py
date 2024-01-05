from pathlib import Path

import pytest
from pydantic import Field, BaseModel

from wunderkafka.serdes.headers import ConfluentClouderaHeadersHandler
from wunderkafka.time import now
from wunderkafka.tests import TestProducer, TestHTTPClient
from wunderkafka.serdes.avro import AvroModelSerializer
from wunderkafka.serdes.store import AvroModelRepo
from wunderkafka.schema_registry import SimpleCache, ClouderaSRClient
from wunderkafka.producers.constructor import HighLevelSerializingProducer


class Signal(BaseModel):
    ts: int = Field(default_factory=now)
    source: str = 'test'
    type: str = 'string'
    id: str = 'string'
    value: str = 'NA'

    class Meta:
        name = 'SignalsTest'


class DefaultKey(BaseModel):
    ts: int = Field(default_factory=now)

    class Meta:
        namespace = "com.localhost"
        name = "SignalsTestKey"


@pytest.fixture
def ts() -> int:
    return 1632128298534


@pytest.fixture
def value_answer() -> bytes:
    return b'\x01\x00\x00\x00\x00\x00\x00\x06\x9c\x00\x00\x00\x01\xcc\xb8\xeb\xa6\x80_\x08test\x0cstring\x0cstring\x04NA'  # noqa: E501


@pytest.fixture
def test_producer() -> TestProducer:
    return TestProducer()


@pytest.fixture
def clean_producer(test_producer: TestProducer, sr_root: Path) -> HighLevelSerializingProducer:
    return HighLevelSerializingProducer(
        producer=test_producer,
        schema_registry=ClouderaSRClient(TestHTTPClient(sr_root), SimpleCache()),
        header_packer=ConfluentClouderaHeadersHandler().pack,
        serializer=AvroModelSerializer(),
        store=AvroModelRepo(),
        mapping={},
    )


def test_avro_producer_moving_parts_value_only(
    clean_producer: HighLevelSerializingProducer,
    test_producer: TestProducer,
    topic: str,
    ts: int,
    value_answer: bytes
) -> None:
    clean_producer.set_target_topic(topic, Signal)
    value = Signal(ts=ts)
    clean_producer.send_message(topic, value)
    [message] = test_producer.sent
    assert message.key is None
    assert message.value == value_answer


def test_avro_producer_moving_parts_value_and_key(
    clean_producer: HighLevelSerializingProducer,
    test_producer: TestProducer,
    value_answer: bytes,
    topic: str,
    ts: int,
) -> None:
    clean_producer.set_target_topic(topic, Signal, DefaultKey)
    key = DefaultKey(ts=ts)
    value = Signal(ts=ts)
    clean_producer.send_message(topic, value, key)
    [message] = test_producer.sent
    assert message.key == b'\x01\x00\x00\x00\x00\x00\x00\x06\x9d\x00\x00\x00\x01\xcc\xb8\xeb\xa6\x80_'
    assert message.value == value_answer
