import pytest


@pytest.fixture
def boostrap_servers() -> str:
    return 'localhost:9093'
