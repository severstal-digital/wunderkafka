from pathlib import Path

import pytest


@pytest.fixture
def topic() -> str:
    return 'testing_wunderkafka'


@pytest.fixture
def sr_root(fixtures_root: Path) -> Path:
    return fixtures_root / 'schema_registry' / 'confluent'


@pytest.fixture
def sr_root_create(sr_root: Path) -> Path:
    return sr_root / 'create'


@pytest.fixture
def sr_root_existing(sr_root: Path) -> Path:
    return sr_root / 'existing'


@pytest.fixture
def sr_root_update(sr_root: Path) -> Path:
    return sr_root / 'update'
