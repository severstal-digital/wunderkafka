import json
from dataclasses import dataclass
from typing import Dict, Union, Optional, List, Tuple

from requests import HTTPError

from wunderkafka.errors import SchemaRegistryLookupException
from wunderkafka.logger import logger
from wunderkafka.structures import SRMeta, SchemaMeta, ParsedHeader
from wunderkafka.schema_registry.abc import AbstractHTTPClient, AbstractSchemaRegistry
from wunderkafka.schema_registry.cache import SimpleCache


SchemaReference = Dict[str, Union[str, int]]
RegistrySchema = Dict[str, Union[str, int, list[SchemaReference]]]


@dataclass(frozen=True)
class RegisteredSchema:
    schema_id: int
    schema: dict
    subject: str
    version: int

    references: Optional[List[SchemaReference]] = None

    @property
    def uniq_key(self) -> Tuple[str, int]:
        return self.subject, self.schema_id

    def as_reference(self) -> SchemaReference:
        return {'name': self.subject, 'subject': self.subject, 'version': self.version}


def _body(
    schema_text: str,
    references: Optional[List[SchemaReference]],
) -> RegistrySchema:
    body: RegistrySchema = {
        'schema': schema_text,
        'schemaType': 'AVRO',
    }
    if references is not None:
        body['references'] = references
    return body


class ConfluentSRClient(AbstractSchemaRegistry):

    def __init__(self, http_client: AbstractHTTPClient, cache: Optional[SimpleCache] = None) -> None:
        self._client = http_client
        self._cache = SimpleCache() if cache is None else cache

    def get_schema_text(self, meta: SchemaMeta) -> str:
        hdr = meta.header
        schema_text = self._cache.get(hdr)
        if schema_text is None:
            logger.debug("Couldn't find header ({0}) in cache, re-requesting...".format(hdr))
            schema_text = self._choose_schema(hdr, meta.subject)
            self._cache.set(hdr, schema_text)
        return schema_text

    def register_schema(self, topic: str, schema_text: str, *, is_key: bool = True) -> SRMeta:
        uid = (topic, schema_text, is_key)
        meta = self._cache.get(uid)
        if meta is None:
            subject = '{0}{1}'.format(topic, '_key' if is_key else '_value')

            subjects = self._client.make_request('subjects/', query={'subjectPrefix': subject})
            if subject not in subjects:
                schema = self._register_schema(subject, schema_text)
            else:
                # ToDo (aa.perelygin): add check compatibility
                #  (https://docs.confluent.io/platform/current/schema-registry/develop/api.html#sr-api-compatibility)
                schema = self._register_new_version(subject, schema_text)

            if isinstance(schema, int):
                schema = self._get_schema(subject, 'latest')

            meta = SRMeta(
                schema_version=schema.version,
                schema_id=schema.schema_id
            )
            self._cache.set(uid, meta)
        return meta

    def _register_schema(
        self,
        subject: str,
        schema_text: str,
        references: Optional[list[SchemaReference]] = None,
        *,
        normalize_schemas: bool = False
    ) -> int:
        response = self._client.make_request(
            'subjects/{0}/versions'.format(subject),
            method='POST',
            body=_body(schema_text, references),
            query={'normalize': normalize_schemas}
        )
        return response['id']

    def _choose_schema(self, hdr: ParsedHeader, subject: str) -> str:
        # https://docs.confluent.io/platform/current/schema-registry/develop/api.html#get--schemas-ids-int-%20id
        try:
            resp = self._client.make_request('schemas/ids/{}'.format(hdr.schema_id), query={'subject': subject})
            return resp['schema']
        except HTTPError:
            raise SchemaRegistryLookupException("Couldn't find schema for {0}".format(hdr))

    def _get_schema(self, subject: str, version_schema: Union[int, str]) -> RegisteredSchema:
        response = self._client.make_request('subjects/{0}/versions/{1}'.format(subject, version_schema))
        schema = json.loads(response['schema'])

        if isinstance(schema, str):
            ref = None
        else:
            ref = schema.get('references')
            if ref is not None:
                del schema['ref']
        schema = RegisteredSchema(
            schema_id=response['id'],
            schema=schema,
            subject=subject,
            version=response['version'],
            references=ref
        )
        return schema

    def _register_new_version(self, subject: str, schema_text: str) -> int:
        client_schema = json.loads(schema_text)
        versions = self._client.make_request('subjects/{0}/versions'.format(subject))
        latest_schema = None
        for ver in versions:
            reg_schema = self._get_schema(subject, ver)
            if client_schema == reg_schema.schema:
                return reg_schema
            latest_schema = reg_schema
        logger.debug('Schema {} not found'.format(subject))

        ref = None
        if latest_schema and not latest_schema.references:
            ref = {
                'name': latest_schema.subject,
                'subject': latest_schema.subject,
                'version': latest_schema.version
            }
        return self._register_schema(subject, schema_text, ref)
