import sys

import pytest

from wunderkafka.factories import (
    AvroConsumer,
    AvroProducer,
    ConsumerConfig,
    ProducerConfig,
    ClouderaSRConfig,
    AvroModelProducer,
)


def test_init_avro_consumer(sr_url):
    AvroConsumer(ConsumerConfig(group_id='test'), ClouderaSRConfig(url=sr_url))


def test_init_avro_producer(sr_url):
    AvroProducer(config=ProducerConfig(), sr_config=ClouderaSRConfig(url=sr_url), mapping={})


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires >= Python3.7")
def test_init_avro_model_producer(sr_url):
    AvroModelProducer(config=ProducerConfig(), sr_config=ClouderaSRConfig(url=sr_url), mapping={})
