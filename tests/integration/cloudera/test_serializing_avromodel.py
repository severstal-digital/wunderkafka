import sys
from pathlib import Path

import pytest
from pydantic import Field, BaseModel

from wunderkafka.time import now
from wunderkafka.tests import TestProducer, TestHTTPClient
from wunderkafka.serdes.avro import AvroModelSerializer, ConfluentClouderaHeadersHandler
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


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires >= Python3.7")
@pytest.mark.parametrize("schema_description", [Signal, (Signal, DefaultKey)])
def test_avro_producer_moving_parts(sr_root: Path, topic: str, schema_description) -> None:
    fixed_ts = 1632128298534
    test_producer = TestProducer()
    producer = HighLevelSerializingProducer(
        producer=test_producer,
        schema_registry=ClouderaSRClient(TestHTTPClient(sr_root), SimpleCache()),
        header_packer=ConfluentClouderaHeadersHandler().pack,
        serializer=AvroModelSerializer(),
        store=AvroModelRepo(),
        mapping={topic: schema_description},
    )

    try:
        value_type, key_type = schema_description
    except TypeError:
        key = None
        value_type = schema_description
    else:
        key = key_type(ts=fixed_ts)
    value = value_type(ts=fixed_ts)

    producer.send_message(topic, value, key)

    [message] = test_producer.sent
    if key is None:
        assert message.key is None
    else:
        assert message.key == b'\x01\x00\x00\x00\x00\x00\x00\x06\x9d\x00\x00\x00\x01\xcc\xb8\xeb\xa6\x80_'
    assert message.value == b'\x01\x00\x00\x00\x00\x00\x00\x06\x9c\x00\x00\x00\x01\xcc\xb8\xeb\xa6\x80_\x08test\x0cstring\x0cstring\x04NA'
