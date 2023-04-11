from pathlib import Path

import pytest


@pytest.fixture
def topic() -> str:
    return 'testing_wunderkafka'


@pytest.fixture
def sr_root_create(fixtures_root: Path) -> Path:
    return fixtures_root / 'schema_registry' / 'confluent' / 'create'


@pytest.fixture
def sr_root_existing(fixtures_root: Path) -> Path:
    return fixtures_root / 'schema_registry' / 'confluent' / 'existing'


@pytest.fixture
def sr_root_update(fixtures_root: Path) -> Path:
    return fixtures_root / 'schema_registry' / 'confluent' / 'update'
