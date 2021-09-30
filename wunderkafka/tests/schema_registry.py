import json
from typing import Any, Union
from pathlib import Path

from wunderkafka.schema_registry.abc import AbstractHTTPClient


class TestHTTPClient(AbstractHTTPClient):

    def __init__(self, root_dir: Union[str, Path]) -> None:
        self._root = Path(root_dir)

    def make_request(self, relative_url: str, method: str = 'GET', body: Any = None, query: Any = None) -> Any:
        filename = self._root / method / '{0}.json'.format(relative_url)
        if relative_url == 'schemas':
            filename = self._root / method / relative_url / body['description'] / '{0}.json'.format(relative_url)
        with open(filename) as fl:
            return json.load(fl)
