from abc import ABC, abstractmethod
from typing import Any, Optional

from wunderkafka.structures import SRMeta, SchemaMeta, SchemaType


class AbstractHTTPClient(ABC):

    @abstractmethod
    def make_request(self, relative_url: str, method: str = 'GET', body: Any = None, query: Any = None) -> Any: ...

    @property
    def base_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None: ...


class AbstractSchemaRegistry(ABC):

    @abstractmethod
    def get_schema_text(self, schema_meta: SchemaMeta) -> str: ...

    @abstractmethod
    def register_schema(self, topic: str, schema_text: str, schema_type: SchemaType, *, is_key: bool = True) -> SRMeta:
        ...
