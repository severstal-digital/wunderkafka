from pathlib import Path

import pytest

from wunderkafka.config.generate import (
    Row,
    group,
    parse,
    read_markdown,
    generate_enums,
    generate_fields,
    generate_models,
)


def read_answer(root: Path, file_name: str) -> list[str]:
    with open(root / 'answers' / file_name) as fl:
        return fl.read().split('\n')[:-1]


@pytest.fixture
def fixture_root() -> Path:
    return Path(__file__).parent.parent / 'fixtures' / 'config'


@pytest.fixture
def configuration_md(fixture_root: Path) -> Path:
    return fixture_root / '1.5.0' / 'CONFIGURATION.md'


@pytest.fixture
def enums(fixture_root: Path) -> list[str]:
    return read_answer(fixture_root, 'enums.py')


@pytest.fixture
def fields(fixture_root: Path) -> list[str]:
    return read_answer(fixture_root, 'fields.py')


@pytest.fixture
def models(fixture_root: Path) -> list[str]:
    return read_answer(fixture_root, 'models.py')


@pytest.fixture
def grouped(configuration_md: Path) -> dict[str, list[Row]]:
    return group(parse(read_markdown(filename=configuration_md)))


def test_enums(grouped: dict[str, list[Row]], enums: list[str]) -> None:
    generated = generate_enums(grouped)
    assert enums == generated


def test_fields(grouped: dict[str, list[Row]], fields: list[str]) -> None:
    generated = generate_fields(grouped)
    assert fields == generated


def test_models(grouped: dict[str, list[Row]], models: list[str]) -> None:
    generated = generate_models(grouped)
    # Multiline for builtin
    assert models == '\n'.join(generated).split('\n')

