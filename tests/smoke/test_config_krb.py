from typing import Any, Dict

import pytest

from wunderkafka import ConsumerConfig, ProducerConfig, SecurityProtocol

RawConfig = Dict[str, Any]


@pytest.fixture
def default_config(boostrap_servers: str) -> RawConfig:
    return {'bootstrap_servers': boostrap_servers}


@pytest.fixture
def non_krb_config(boostrap_servers: str) -> RawConfig:
    return {
        'bootstrap_servers': boostrap_servers,
        'sasl_username': 'user',
        'sasl_password': 'password',
        'security_protocol': SecurityProtocol.sasl_ssl,
        'sasl_mechanism': 'SCRAM-SHA-512',
    }


@pytest.fixture
def krb_config(boostrap_servers: str) -> RawConfig:
    return {
        'bootstrap_servers': boostrap_servers,
        'sasl_username': 'user',
        'sasl_password': 'password',
        'security_protocol': SecurityProtocol.sasl_ssl,
    }


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
