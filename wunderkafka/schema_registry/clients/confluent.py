from __future__ import annotations

from typing import Any, Optional

from typing_extensions import Protocol
from confluent_kafka.schema_registry import Schema
from confluent_kafka.schema_registry import SchemaRegistryClient as ConfluentSchemaRegistryClient

from wunderkafka.compat import ParamSpec
from wunderkafka.structures import SRMeta, SchemaMeta, SchemaType
from wunderkafka.schema_registry import SimpleCache
from wunderkafka.schema_registry.abc import AbstractHTTPClient, AbstractSchemaRegistry

P = ParamSpec('P')


class ConfluentRestClient(Protocol):

    def get(self, url: str, query: Optional[dict] = None) -> Any:
        ...

    def post(self, url: str, body: Optional[str], **kwargs: Any) -> Any:
        ...

    def delete(self, url: str) -> Any:
        ...

    def put(self, url: str, body: Optional[str] = None) -> Any:
        ...

    def send_request(self, url: str, method: str, body: Optional[str] = None, query: Optional[dict] = None) -> Any:
        ...

    def _close(self) -> None:
        ...


class Adapter(object):
    def __init__(self, http_client: AbstractHTTPClient) -> None:
        self._client = http_client

    def get(self, url: str, query: Optional[dict] = None) -> Any:
        return self._client.make_request(url, query=query)

    def post(self, url: str, body: Optional[str], **_: Any) -> Any:
        return self._client.make_request(url, method='POST', body=body)

    def delete(self, url: str) -> Any:
        return self._client.make_request(url, method='DELETE')

    def put(self, url: str, body: Optional[str] = None) -> Any:
        return self._client.make_request(url, method='PUT', body=body)

    def send_request(self, url: str, method: str, body: Optional[str] = None, query: Optional[dict] = None) -> Any:
        return self._client.make_request(url, method, body=body, query=query)

    def _close(self) -> None:
        return self._client.close()


class SchemaRegistryClient(ConfluentSchemaRegistryClient):

    @classmethod
    def from_client(cls, http_client: AbstractHTTPClient, *args: P.args, **kwargs: P.kwargs) -> SchemaRegistryClient:
        # Minimal initialization as we will override a client with our own
        client = cls({'url': http_client.base_url, **kwargs})
        client._rest_client = Adapter(http_client)
        return client


class ConfluentSRClient(AbstractSchemaRegistry):

    def __init__(
        self,
        http_client: AbstractHTTPClient,
        _: Optional[SimpleCache] = None,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        self.client = SchemaRegistryClient.from_client(http_client, *args, **kwargs)

    def get_schema_text(self, meta: SchemaMeta) -> str:
        schema = self.client.get_schema(meta.header.schema_id)
        return schema.schema_str

    def register_schema(self, topic: str, schema_text: str, schema_type: SchemaType, *, is_key: bool = True) -> SRMeta:
        # FixMe (tribunsky.kir): lack of symmetry here - SchemaMeta knows about different vendors, but not vice versa.
        subject = '{0}-{1}'.format(topic, 'key' if is_key else 'value')
        schema_id = self.client.register_schema(subject, Schema(schema_text, schema_type=schema_type))
        return SRMeta(schema_id, schema_version=None)
