from typing import Any, Optional, Union

from wunderkafka.errors import SchemaRegistryLookupException
from wunderkafka.logger import logger
from wunderkafka.schema_registry.abc import AbstractHTTPClient, AbstractSchemaRegistry
from wunderkafka.schema_registry.cache import AlwaysEmptyCache, SimpleCache
from wunderkafka.serdes.headers import PROTOCOLS
from wunderkafka.structures import ParsedHeader, SchemaMeta, SchemaType, SRMeta


def prepare_schemas_for_caching(
    versions: dict[str, list[dict[str, Optional[Union[int, str]]]]],
) -> dict[ParsedHeader, str]:
    schemas_to_header_mapping = {}
    for schema in versions['entities']:
        txt = schema['schemaText']
        if not isinstance(txt, str):
            raise ValueError(f'Provided SchemaText is not str: {schema}')
        meta_id = schema['schemaMetadataId']
        if not isinstance(meta_id, int):
            raise ValueError(f'Wrong schemaMetadataId (not int): {schema}')
        schema_version = schema['version']
        if not isinstance(schema_version, int):
            raise ValueError(f'Wrong schema version (not int): {schema}')
        new_header_v1 = ParsedHeader(
            protocol_id=1,
            meta_id=meta_id,
            schema_version=schema_version,
            schema_id=None,
            size=PROTOCOLS[1].header_size + 1,
        )
        schema_id = schema['id']
        if not isinstance(schema_id, int):
            raise ValueError(f'Wrong schema id (not int): {schema}')
        new_header_v2 = ParsedHeader(
            protocol_id=2,
            meta_id=None,
            schema_version=None,
            schema_id=schema_id,
            size=PROTOCOLS[2].header_size + 1,
        )
        new_header_v3 = ParsedHeader(
            protocol_id=3,
            meta_id=None,
            schema_version=None,
            schema_id=schema_id,
            size=PROTOCOLS[3].header_size + 1,
        )
        for new_header in (new_header_v1, new_header_v2, new_header_v3):
            schemas_to_header_mapping[new_header] = txt
    return schemas_to_header_mapping


class ClouderaSRClient(AbstractSchemaRegistry):

    def __init__(self, http_client: AbstractHTTPClient, cache: Optional[SimpleCache] = None) -> None:
        self._client = http_client
        self._cache = AlwaysEmptyCache() if cache is None else cache
        self._requests_count = 0

    @property
    def requests_count(self) -> int:
        return self._requests_count

    def _send_request_for_schema(self, meta: SchemaMeta) -> Any:
        versions = self._client.get(f'schemas/{meta.subject}/versions')
        self._requests_count += 1
        return versions

    def _create_meta(self, subject: str) -> int:
        body = {
            'type': 'avro',
            'schemaGroup': 'Kafka',
            'name': subject,
            'description': subject,
            'compatibility': 'BACKWARD',
            'validationLevel': 'ALL',
        }
        return self._client.post('schemas', body=body)

    def _create_schema(self, subject: str, schema_text: str) -> int:
        body = {
            "description": subject,
            # TypeError: Object of type 'mappingproxy' is not JSON serializable
            # https://github.com/confluentinc/confluent-kafka-python/issues/610
            "schemaText": schema_text,
        }
        query = {'branch': 'MASTER'}
        return self._client.post(f'schemas/{subject}/versions', body=body, query=query)

    def get_schema_text(self, meta: SchemaMeta) -> str:
        # ToDo (tribunsky.kir): arguably, the best key is BINARY header, not dataclass.
        # ToDo (tribunsky.kir): ineffective caching. When we get response with list of schemas,
        #                       we can do better: pre-generate all possible metas and keep texts
        schema_text = self._cache.get(meta.header)
        if schema_text is not None:
            return schema_text
        logger.debug(f"Couldn't find header ({meta.header}) in cache, re-requesting...")
        versions = self._send_request_for_schema(meta)
        for hdr, txt in prepare_schemas_for_caching(versions).items():
            self._cache.set(hdr, txt)
        schema_text = self._cache.get(meta.header)
        if schema_text is None:
            error_message = f"Couldn't find schema for {meta.header}"
            logger.error(error_message)
            for schema in versions['entities']:
                logger.warning(f'\tschema: {schema}')
            raise SchemaRegistryLookupException(error_message)
        return schema_text

    # ToDo (tribunsky.kir): here and in producers/constructor:
    #                       - make hypothetical meta + prop for subject
    #                       - symmetry with get_schema_text
    def register_schema(self, topic: str, schema_text: str, schema_type: SchemaType, *, is_key: bool = True) -> SRMeta:
        uid = (topic, schema_text, is_key)
        meta = self._cache.get(uid)
        if meta is None:
            suffix = ':k' if is_key else ''
            subject = f'{topic}{suffix}'
            # ToDo (tribunsky.kir): three queries is bad. Either we should know protocol id,
            #                       e.g. to skip last query (we do not need id always)
            meta_id = self._create_meta(subject)
            schema_version = self._create_schema(subject, schema_text)
            versions = self._client.get(f'schemas/{subject}/versions')
            for mt in versions['entities']:
                if mt['schemaMetadataId'] == meta_id and mt['version'] == schema_version:
                    meta = SRMeta(
                        meta_id=meta_id,
                        schema_version=schema_version,
                        schema_id=mt['id']
                    )
            self._cache.set(uid, meta)
        return meta
