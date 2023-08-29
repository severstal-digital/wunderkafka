from tests.smoke.conftest import RawConfig
from wunderkafka import ConsumerConfig, ProducerConfig


def test_default_consumer_not_requires_krb(default_config: RawConfig) -> None:
    config = ConsumerConfig(group_id='my_group', **default_config)
    assert config.requires_kerberos is False


def test_default_producer_not_requires_krb(default_config: RawConfig) -> None:
    config = ProducerConfig(**default_config)
    assert config.requires_kerberos is False


def test_consumer_requires_krb(krb_config: RawConfig) -> None:
    config = ConsumerConfig(group_id='my_group', **krb_config)
    assert config.requires_kerberos is True


def test_producer_requires_krb(krb_config: RawConfig) -> None:
    config = ProducerConfig(**krb_config)
    assert config.requires_kerberos is True


def test_consumer_not_requires_krb(non_krb_config: RawConfig) -> None:
    config = ConsumerConfig(group_id='my_group', **non_krb_config)
    assert config.requires_kerberos is False


def test_producer_not_requires_krb(non_krb_config: RawConfig) -> None:
    config = ProducerConfig(**non_krb_config)
    assert config.requires_kerberos is False
