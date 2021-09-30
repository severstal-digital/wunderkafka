import os
from pathlib import Path

import pytest


@pytest.fixture
def sr_root() -> Path:
    return Path(os.path.dirname(__file__)) / '..' / 'fixtures' / 'schema_registry'

