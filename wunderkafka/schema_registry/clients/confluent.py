from __future__ import annotations

from typing import Optional, Any
from typing_extensions import Protocol
from confluent_kafka.schema_registry import SchemaRegistryClient as ConfluentSchemaRegistryClient, Schema

from wunderkafka.schema_registry import SimpleCache
from wunderkafka.structures import SRMeta, SchemaMeta
from wunderkafka.schema_registry.abc import AbstractHTTPClient, AbstractSchemaRegistry


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
    def from_client(cls, http_client: AbstractHTTPClient) -> SchemaRegistryClient:
        # Minimal initialization as we will override client with our own
        client = cls({'url': http_client.base_url})
        client._rest_client = Adapter(http_client)
        return client


class ConfluentSRClient(AbstractSchemaRegistry):

    def __init__(self, http_client: AbstractHTTPClient, _: Optional[SimpleCache] = None) -> None:
        self.client = SchemaRegistryClient.from_client(http_client)

    def get_schema_text(self, meta: SchemaMeta) -> str:
        schema = self.client.get_schema(meta.header.schema_id)
        return schema.schema_str

    def register_schema(self, topic: str, schema_text: str, *, is_key: bool = True) -> SRMeta:
        # FixMe (tribunsky.kir): lack of symmetry here - SchemaMeta knows about different vendors, but not vice versa.
        subject = '{0}{1}'.format(topic, '_key' if is_key else '_value')
        schema_id = self.client.register_schema(subject, Schema(schema_text, schema_type='AVRO'))
        return SRMeta(schema_id, schema_version=None)
