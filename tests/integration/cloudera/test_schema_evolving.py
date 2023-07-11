from pathlib import Path

import pytest

from wunderkafka.tests import TestHTTPClient
from wunderkafka.errors import SchemaRegistryLookupException
from wunderkafka.structures import SchemaMeta, ParsedHeader
from wunderkafka.schema_registry import SimpleCache, ClouderaSRClient


@pytest.fixture
def client(sr_root: Path) -> ClouderaSRClient:
    return ClouderaSRClient(TestHTTPClient(sr_root), SimpleCache())


@pytest.fixture
def topic() -> str:
    return 'test_signals'


@pytest.fixture
def schema_v1(topic: str) -> SchemaMeta:
    return SchemaMeta(
        topic=topic,
        is_key=False,
        header=ParsedHeader(protocol_id=1, meta_id=1692, schema_id=None, schema_version=1, size=13),
    )


@pytest.fixture
def schema_v2(topic: str) -> SchemaMeta:
    return SchemaMeta(
        topic=topic,
        is_key=False,
        header=ParsedHeader(protocol_id=1, meta_id=1692, schema_id=None, schema_version=2, size=13),
    )


def test_runtime_evolving(client: ClouderaSRClient, schema_v1: SchemaMeta, schema_v2: SchemaMeta) -> None:
    assert client.get_schema_text(schema_v1)
    with pytest.raises(SchemaRegistryLookupException):
        client.get_schema_text(schema_v2)
    assert client.requests_count == 2
