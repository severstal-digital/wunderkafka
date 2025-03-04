from abc import ABC, abstractmethod
from typing import Any

from wunderkafka.structures import SchemaMeta, SchemaType, SRMeta


# TODO: replace with http.HTTPMethod when we drop python 3.10
class HTTPMethod:
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'


class AbstractHTTPClient(ABC):

    @abstractmethod
    def make_request(self, relative_url: str, method: str = 'GET', body: Any = None, query: Any = None) -> Any: ...

    @property
    def base_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None: ...

    def get(self, relative_url: str, body: Any = None, query: Any = None, **_: Any) -> Any:
        return self.make_request(relative_url, HTTPMethod.GET, body, query)

    def post(self, relative_url: str, body: Any = None, query: Any = None, **_: Any) -> Any:
        return self.make_request(relative_url, HTTPMethod.POST, body, query)

    def put(self, relative_url: str, body: Any = None, query: Any = None, **_: Any) -> Any:
        return self.make_request(relative_url, HTTPMethod.PUT, body, query)

    def patch(self, relative_url: str, body: Any = None, query: Any = None, **_: Any) -> Any:
        return self.make_request(relative_url, HTTPMethod.PATCH, body, query)

    def delete(self, relative_url: str, body: Any = None, query: Any = None, **_: Any) -> Any:
        return self.make_request(relative_url, HTTPMethod.DELETE, body, query)


class AbstractSchemaRegistry(ABC):

    @abstractmethod
    def get_schema_text(self, schema_meta: SchemaMeta) -> str: ...

    @abstractmethod
    def register_schema(self, topic: str, schema_text: str, schema_type: SchemaType, *, is_key: bool = True) -> SRMeta:
        ...
