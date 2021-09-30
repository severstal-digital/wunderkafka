import pytest


@pytest.fixture
def topic() -> str:
    return 'test_signals'


@pytest.fixture
def sr_url() -> str:
    return 'http://localhost:7790/api/v1/schemaregistry'
