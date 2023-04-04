import sys

import pytest

from wunderkafka.factories import AvroConsumer, AvroProducer, ConsumerConfig, ProducerConfig, AvroModelProducer
from wunderkafka.config.schema_registry import SRConfig


def test_init_avro_consumer(sr_url: str) -> None:
    AvroConsumer(ConsumerConfig(group_id='test', sr=SRConfig(url=sr_url)))


def test_init_avro_producer(sr_url: str) -> None:
    AvroProducer(config=ProducerConfig(sr=SRConfig(url=sr_url)), mapping={})


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires >= Python3.7")
def test_init_avro_model_producer(sr_url: str) -> None:
    AvroModelProducer(config=ProducerConfig(sr=SRConfig(url=sr_url)), mapping={})
