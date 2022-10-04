from typing import Any, Dict, List, Union, Optional

from wunderkafka.errors import SchemaRegistryLookupException
from wunderkafka.logger import logger
from wunderkafka.structures import SRMeta, SchemaMeta, ParsedHeader
from wunderkafka.schema_registry.abc import AbstractHTTPClient, AbstractSchemaRegistry
from wunderkafka.schema_registry.cache import SimpleCache, AlwaysEmptyCache


# ToDo (tribunsky.kir): we can cache all schemas at once for every header (key)
def choose_schema(header: ParsedHeader, versions: Dict[str, List[Dict[str, Optional[Union[int, str]]]]]) -> str:
    if header.protocol_id == 0:
        raise NotImplementedError("Didn't check with confluent for now")

    if header.protocol_id == 1:
        for schema in versions['entities']:
            if schema['schemaMetadataId'] == header.meta_id and schema['version'] == header.schema_version:
                # ToDo: use model to describe SchemaRegistry response.
                txt = schema['schemaText']
                if isinstance(txt, str):
                    return txt

    if header.protocol_id in {2, 3}:
        for schema in versions['entities']:
            if schema['id'] == header.schema_id:
                txt = schema['schemaText']
                if isinstance(txt, str):
                    return txt

    raise SchemaRegistryLookupException("Couldn't find schema for {0}".format(header))


class ClouderaSRClient(AbstractSchemaRegistry):

    def __init__(self, http_client: AbstractHTTPClient, cache: Optional[SimpleCache] = None) -> None:
        self._client = http_client
        self._cache = AlwaysEmptyCache() if cache is None else cache

    def _send_request_for_schema(self, meta: SchemaMeta) -> Any:
        subject = meta.subject
        versions = self._cache.get(subject)
        if versions is None:
            versions = self._client.make_request('schemas/{0}/versions'.format(subject))
            self._cache.set(subject, versions)
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
        hdr = meta.header
        schema_text = self._cache.get(hdr)
        if schema_text is None:
            logger.debug("Couldn't find header ({0}) in cache, re-requesting...".format(hdr))
            versions = self._send_request_for_schema(meta)
            schema_text = choose_schema(hdr, versions)
            self._cache.set(hdr, schema_text)
        return schema_text

    # ToDo (tribunsky.kir): here and in producers/constructor:
    #                       - make hypotehtical meta + prop for subject
    #                       - symmetry with get_schema_text
    def register_schema(self, topic: str, schema_text: str, *, is_key: bool = True) -> SRMeta:
        uid = (topic, schema_text, is_key)
        meta = self._cache.get(uid)
        if meta is None:
            suffix = ':k' if is_key else ''
            subject = '{0}{1}'.format(topic, suffix)
            # ToDo (tribunsky.kir): three queris is bad. Either we should know protocol id,
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

    # def load_all(self):
    #     response = self._client.make_request('schemas')
    #     entities = response['entities']
    #     logger.info('Got {0} schemas'.format(len(entities)))
