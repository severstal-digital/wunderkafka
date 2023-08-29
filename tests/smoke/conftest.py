from typing import Dict, Any

import pytest

from wunderkafka import SecurityProtocol

RawConfig = Dict[str, Any]


@pytest.fixture
def boostrap_servers() -> str:
    return 'localhost:9093'


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