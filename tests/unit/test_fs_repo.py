import json
from typing import Any, Dict
from pathlib import Path

import pytest

from wunderkafka.serdes.store import SchemaFSRepo


@pytest.fixture
def repo() -> SchemaFSRepo:
    return SchemaFSRepo()


@pytest.fixture
def fs_root_dir(fixtures_root: Path) -> Path:
    return fixtures_root / 'fs_repo'


@pytest.fixture
def answer_json() -> Dict[str, Any]:
    return {
     "type": "record",
     "name": "exampleSchema",
     "fields": [
      {
       "name": "name",
       "type": "string",
       "default": ""
      },
      {
       "name": "value",
       "type": "string",
       "default": ""
      }
     ]
    }


@pytest.mark.parametrize('key_schema_path,value_schema_path', [('key.avsc', 'value.avsc')])
def test_fs_repo(
    repo: SchemaFSRepo,
    topic: str,
    key_schema_path: str,
    value_schema_path: str,
    fs_root_dir: Path,
    answer_json: Dict[str, Any]
) -> None:
    repo.add(topic, fs_root_dir / value_schema_path, fs_root_dir / key_schema_path)
    key_schema = repo.get(topic, is_key=True)
    assert key_schema is not None
    assert key_schema.text == '"long"'
    value_schema = repo.get(topic)
    assert value_schema is not None
    assert json.loads(value_schema.text) == answer_json
