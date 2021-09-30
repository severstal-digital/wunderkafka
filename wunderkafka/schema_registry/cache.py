from typing import Any, Dict


class SimpleCache(object):
    def __init__(self) -> None:
        self._store: Dict[Any, Any] = {}

    def get(self, key: Any) -> Any:
        return self._store.get(key)

    def set(self, key: Any, value: Any) -> Any:
        self._store[key] = value


class AlwaysEmptyCache(SimpleCache):
    def set(self, key: Any, value: Any) -> Any:
        return None
