from typing import Any

import pytest
from pytest import FixtureRequest

from wunderkafka import SecurityProtocol

RawConfig = dict[str, Any]


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


@pytest.fixture(params=[SecurityProtocol.sasl_ssl, SecurityProtocol.sasl_plaintext])
def krb_config(request: FixtureRequest, boostrap_servers: str) -> RawConfig:
    return {
        'bootstrap_servers': boostrap_servers,
        'sasl_kerberos_keytab': 'user.keytab',
        'security_protocol': request.param,
    }
