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
    assert repo.get(topic, is_key=True).text == '"long"'
    assert json.loads(repo.get(topic).text) == answer_json
