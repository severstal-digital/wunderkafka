import pytest
from pydantic import ValidationError

from wunderkafka import SRConfig, BytesConsumer, BytesProducer, ConsumerConfig, ProducerConfig


@pytest.fixture
def boostrap_servers() -> str:
    return 'localhost:9093'


def test_init_consumer(boostrap_servers: str) -> None:
    config = ConsumerConfig(group_id='my_group', bootstrap_servers=boostrap_servers)
    consumer = BytesConsumer(config)
    print(consumer)

    with pytest.raises(AttributeError):
        consumer.config = ConsumerConfig(                                                                 # type: ignore
            group_id='my_other_group',
            bootstrap_servers=boostrap_servers,
        )
    assert consumer.config == config

    consumer.close()


def test_init_producer(boostrap_servers: str) -> None:
    config = ProducerConfig(bootstrap_servers=boostrap_servers)
    BytesProducer(config)


def test_sr_required_url() -> None:
    with pytest.raises(ValidationError):
        SRConfig()


def test_group_id_required() -> None:
    with pytest.raises(ValidationError):
        ConsumerConfig()
