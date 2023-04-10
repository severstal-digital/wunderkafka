import sys
from pathlib import Path
from typing import Optional, Type

import pytest
from pydantic import BaseModel

from wunderkafka.tests import TestProducer, TestHTTPClient
from wunderkafka.serdes.avro import AvroModelSerializer, ConfluentClouderaHeadersHandler
from wunderkafka.serdes.store import AvroModelRepo
from wunderkafka.schema_registry import SimpleCache, ConfluentSRClient
from wunderkafka.producers.constructor import HighLevelSerializingProducer


class Event(BaseModel):
    id: Optional[int]
    ts: Optional[int]

    class Meta:
        namespace = "any.data"


class EvolvedEvent(Event):
    description: Optional[str] = None
    info: Optional[str] = 'test'


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires >= Python3.7")
def test_avro_producer_create_schema(sr_root_create: Path, topic: str, schema_description: Type[Event] = Event) -> None:
    fixed_ts = 1632128298534
    test_producer = TestProducer()
    producer = HighLevelSerializingProducer(
        producer=test_producer,
        schema_registry=ConfluentSRClient(TestHTTPClient(sr_root_create), SimpleCache()),
        header_packer=ConfluentClouderaHeadersHandler().pack,
        serializer=AvroModelSerializer(),
        store=AvroModelRepo(),
        mapping={topic: schema_description},
        protocol_id=0,
    )

    key = None
    value = schema_description(ts=fixed_ts)

    producer.send_message(topic, value, key)

    [message] = test_producer.sent

    assert message.key is None
    assert message.value == b'\x00\x00\x00\x00\x14\x02\x00\xcc\xb8\xeb\xa6\x80_'


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires >= Python3.7")
def test_avro_producer_existing_schema(
    sr_root_existing: Path,
    topic: str,
    schema_description: Type[Event] = Event,
) -> None:
    fixed_ts = 1632128298534
    test_producer = TestProducer()
    producer = HighLevelSerializingProducer(
        producer=test_producer,
        schema_registry=ConfluentSRClient(TestHTTPClient(sr_root_existing), SimpleCache()),
        header_packer=ConfluentClouderaHeadersHandler().pack,
        serializer=AvroModelSerializer(),
        store=AvroModelRepo(),
        mapping={topic: schema_description},
        protocol_id=0,
    )

    key = None
    value = schema_description(ts=fixed_ts)

    producer.send_message(topic, value, key)

    [message] = test_producer.sent

    assert message.key is None
    assert message.value == b'\x00\x00\x00\x00\x14\x02\x00\xcc\xb8\xeb\xa6\x80_'


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires >= Python3.7")
def test_avro_producer_update_schema(
    sr_root_update: Path,
    topic: str,
    schema_description: Type[EvolvedEvent] = EvolvedEvent,
) -> None:
    fixed_ts = 1632128298534
    test_producer = TestProducer()
    producer = HighLevelSerializingProducer(
        producer=test_producer,
        schema_registry=ConfluentSRClient(TestHTTPClient(sr_root_update), SimpleCache()),
        header_packer=ConfluentClouderaHeadersHandler().pack,
        serializer=AvroModelSerializer(),
        store=AvroModelRepo(),
        mapping={topic: schema_description},
        protocol_id=0,
    )

    key = None
    value = schema_description(ts=fixed_ts)

    producer.send_message(topic, value, key)

    [message] = test_producer.sent

    assert message.key is None
    assert message.value == b'\x00\x00\x00\x00\x15\x02\x00\xcc\xb8\xeb\xa6\x80_\x00\x00\x08test'
