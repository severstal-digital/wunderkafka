from wunderkafka.config.schema_registry import SRConfig
from wunderkafka.factories.avro import AvroConsumer, AvroModelProducer, AvroProducer, ConsumerConfig, ProducerConfig


def test_init_avro_consumer(sr_url: str) -> None:
    AvroConsumer(ConsumerConfig(group_id='test', sr=SRConfig(url=sr_url)))


def test_init_avro_producer(sr_url: str) -> None:
    AvroProducer(config=ProducerConfig(sr=SRConfig(url=sr_url)), mapping={})


def test_init_avro_model_producer(sr_url: str) -> None:
    AvroModelProducer(config=ProducerConfig(sr=SRConfig(url=sr_url)), mapping={})
