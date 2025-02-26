from pathlib import Path
from typing import Optional

from pydantic import UUID4, BaseModel

from wunderkafka.producers.constructor import HighLevelSerializingProducer
from wunderkafka.serdes.schemaless.string.serializers import StringSerializer
from wunderkafka.tests import TestProducer


class Image(BaseModel):
    id: Optional[UUID4] = None
    path: Optional[str] = None


def test_string_producer_string_key_no_schema(sr_root_existing: Path, topic: str) -> None:
    test_producer = TestProducer()
    producer = HighLevelSerializingProducer(
        producer=test_producer,
        schema_registry=None,
        header_packer=None,
        value_serializer=StringSerializer(),
        key_serializer=StringSerializer(),
        mapping={topic: (str, str)},
        protocol_id=0,
    )

    key = "714fc713-37ff-4477-9157-cb4f14b63e1a"
    value = "/var/folders/x5/zlpmj3915pqfj5lhnlq5qwkm0000gn/T/tmprq2rktq3"

    producer.send_message(topic, value, key)

    [message] = test_producer.sent

    assert message.key == b'714fc713-37ff-4477-9157-cb4f14b63e1a'
    assert message.value == b'/var/folders/x5/zlpmj3915pqfj5lhnlq5qwkm0000gn/T/tmprq2rktq3'
