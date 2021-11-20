import os
from pathlib import Path

import pytest


@pytest.fixture
def topic() -> str:
    return 'test_signals'


@pytest.fixture
def sr_url() -> str:
    return 'http://localhost:7790/api/v1/schemaregistry'


@pytest.fixture
def fixtures_root() -> Path:
    return Path(os.path.dirname(__file__)) / 'fixtures'
