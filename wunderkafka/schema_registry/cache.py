from typing import Any


class SimpleCache:
    def __init__(self) -> None:
        self._store: dict[Any, Any] = {}

    def get(self, key: Any) -> Any:
        return self._store.get(key)

    def set(self, key: Any, value: Any) -> Any:
        self._store[key] = value


class AlwaysEmptyCache(SimpleCache):
    def set(self, key: Any, value: Any) -> Any:
        return None
