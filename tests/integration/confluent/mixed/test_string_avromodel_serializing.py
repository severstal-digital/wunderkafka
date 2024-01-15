from typing import Optional
from pathlib import Path

from pydantic import BaseModel, UUID4

from wunderkafka.serdes.avromodel.serializers import AvroModelSerializer
from wunderkafka.serdes.store import AvroModelRepo

from wunderkafka.serdes.string.serializers import StringSerializer
from wunderkafka.serdes.headers import ConfluentClouderaHeadersHandler
from wunderkafka.tests import TestProducer, TestHTTPClient
from wunderkafka.schema_registry import SimpleCache, ConfluentSRClient
from wunderkafka.producers.constructor import HighLevelSerializingProducer


class Image(BaseModel):
    id: UUID4
    path: Optional[str] = None


def test_avro_producer_string_key_create_schema(sr_root_existing: Path) -> None:
    topic = 'testing_avro_str_producer'
    test_producer = TestProducer()
    sr_client = ConfluentSRClient(TestHTTPClient(sr_root_existing), SimpleCache())
    producer = HighLevelSerializingProducer(
        producer=test_producer,
        schema_registry=sr_client,
        header_packer=ConfluentClouderaHeadersHandler().pack,
        value_serializer=AvroModelSerializer(AvroModelRepo()),
        key_serializer=StringSerializer(),
        mapping={topic: (Image, str)},
        protocol_id=0,
    )

    key = "714fc713-37ff-4477-9157-cb4f14b63e1a"
    value = Image(
        id="714fc713-37ff-4477-9157-cb4f14b63e1a",
        path="/var/folders/x5/zlpmj3915pqfj5lhnlq5qwkm0000gn/T/tmprq2rktq3",
    )

    producer.send_message(topic, value, key)

    [message] = test_producer.sent

    assert message.key == b'714fc713-37ff-4477-9157-cb4f14b63e1a'
    assert message.value == b'\x00\x00\x00\x00\x13H714fc713-37ff-4477-9157-cb4f14b63e1a\x02x/var/folders/x5/zlpmj3915pqfj5lhnlq5qwkm0000gn/T/tmprq2rktq3'
