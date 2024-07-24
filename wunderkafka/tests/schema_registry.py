import json
from typing import Any, Union
from pathlib import Path
from urllib.parse import urlparse

from wunderkafka.schema_registry.abc import AbstractHTTPClient


class TestHTTPClient(AbstractHTTPClient):

    def __init__(self, root_dir: Union[str, Path]) -> None:
        self._root = Path(root_dir)

    def make_request(self, relative_url: str, method: str = 'GET', body: Any = None, query: Any = None) -> Any:
        # ToDo (tribunsky.kir): rise up actual SR, stop using FS here.
        parsed = urlparse(relative_url)
        filename = self._root / method / '{0}.json'.format(parsed.path)
        if parsed.path == 'schemas':
            filename = self._root / method / relative_url / body['description'] / '{0}.json'.format(parsed.path)
        with open(filename) as fl:
            return json.load(fl)

    def close(self) -> None:
        ...

    @property
    def base_url(self) -> str:
        return 'http://localhost'
