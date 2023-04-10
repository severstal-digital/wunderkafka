from pathlib import Path

import pytest


@pytest.fixture
def sr_root(fixtures_root: Path) -> Path:
    return fixtures_root / 'schema_registry' / 'cloudera'
