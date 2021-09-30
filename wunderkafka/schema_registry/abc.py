from abc import ABC, abstractmethod
from typing import Any

from wunderkafka.structures import SRMeta, SchemaMeta


class AbstractHTTPClient(ABC):

    @abstractmethod
    def make_request(self, relative_url: str, method: str = 'GET', body: Any = None, query: Any = None) -> Any: ...


class AbstractSchemaRegistry(ABC):

    @abstractmethod
    def get_schema_text(self, schema_meta: SchemaMeta) -> str: ...

    @abstractmethod
    def register_schema(self, topic: str, schema_text: str, *, is_key: bool = True) -> SRMeta: ...
