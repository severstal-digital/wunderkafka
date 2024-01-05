from typing import Any, Dict, List, Union, Optional

from wunderkafka.errors import SchemaRegistryLookupException
from wunderkafka.logger import logger
from wunderkafka.structures import SRMeta, SchemaMeta, ParsedHeader
from wunderkafka.schema_registry.abc import AbstractHTTPClient, AbstractSchemaRegistry
from wunderkafka.serdes.headers import PROTOCOLS
from wunderkafka.schema_registry.cache import SimpleCache, AlwaysEmptyCache


def prepare_schemas_for_caching(
    versions: Dict[str, List[Dict[str, Optional[Union[int, str]]]]],
) -> Dict[ParsedHeader, str]:
    schemas_to_header_mapping = {}
    for schema in versions['entities']:
        txt = schema['schemaText']
        if not isinstance(txt, str):
            raise ValueError('Provided SchemaText is not str: {0}'.format(schema))
        meta_id = schema['schemaMetadataId']
        if not isinstance(meta_id, int):
            raise ValueError('Wrong schemaMetadataId (not int): {0}'.format(schema))
        schema_version = schema['version']
        if not isinstance(schema_version, int):
            raise ValueError('Wrong schema version (not int): {0}'.format(schema))
        new_header_v1 = ParsedHeader(
            protocol_id=1,
            meta_id=meta_id,
            schema_version=schema_version,
            schema_id=None,
            size=PROTOCOLS[1].header_size + 1,
        )
        schema_id = schema['id']
        if not isinstance(schema_id, int):
            raise ValueError('Wrong schema id (not int): {0}'.format(schema))
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
        versions = self._client.make_request('schemas/{0}/versions'.format(meta.subject))
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
        return self._client.make_request('schemas', method='POST', body=body)

    def _create_schema(self, subject: str, schema_text: str) -> int:
        body = {
            "description": subject,
            # TypeError: Object of type 'mappingproxy' is not JSON serializable
            # https://github.com/confluentinc/confluent-kafka-python/issues/610
            "schemaText": schema_text,
        }
        query = {'branch': 'MASTER'}
        return self._client.make_request('schemas/{0}/versions'.format(subject), method='POST', body=body, query=query)

    def get_schema_text(self, meta: SchemaMeta) -> str:
        # ToDo (tribunsky.kir): arguably, the best key is BINARY header, not dataclass.
        # ToDo (tribunsky.kir): ineffective caching. When we get response with list of schemas,
        #                       we can do better: pre-generate all possible metas and keep texts
        schema_text = self._cache.get(meta.header)
        if schema_text is not None:
            return schema_text
        logger.debug("Couldn't find header ({0}) in cache, re-requesting...".format(meta.header))
        versions = self._send_request_for_schema(meta)
        for hdr, txt in prepare_schemas_for_caching(versions).items():
            self._cache.set(hdr, txt)
        schema_text = self._cache.get(meta.header)
        if schema_text is None:
            error_message = "Couldn't find schema for {0}".format(meta.header)
            logger.error(error_message)
            for schema in versions['entities']:
                logger.warning('\tschema: {0}'.format(schema))
            raise SchemaRegistryLookupException(error_message)
        return schema_text

    # ToDo (tribunsky.kir): here and in producers/constructor:
    #                       - make hypothetical meta + prop for subject
    #                       - symmetry with get_schema_text
    def register_schema(self, topic: str, schema_text: str, *, is_key: bool = True) -> SRMeta:
        uid = (topic, schema_text, is_key)
        meta = self._cache.get(uid)
        if meta is None:
            suffix = ':k' if is_key else ''
            subject = '{0}{1}'.format(topic, suffix)
            # ToDo (tribunsky.kir): three queries is bad. Either we should know protocol id,
            #                       e.g. to skip last query (we do not need id always)
            meta_id = self._create_meta(subject)
            schema_version = self._create_schema(subject, schema_text)
            versions = self._client.make_request('schemas/{0}/versions'.format(subject))
            for mt in versions['entities']:
                if mt['schemaMetadataId'] == meta_id and mt['version'] == schema_version:
                    meta = SRMeta(
                        meta_id=meta_id,
                        schema_version=schema_version,
                        schema_id=mt['id']
                    )
            self._cache.set(uid, meta)
        return meta
