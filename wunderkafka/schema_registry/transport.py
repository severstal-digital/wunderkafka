import os
import json
from typing import Any

import requests
from loguru import logger
from requests_kerberos import HTTPKerberosAuth

from wunderkafka.schema_registry.abc import AbstractHTTPClient
from wunderkafka.config.schema_registry import ClouderaSRConfig


class KerberizableHTTPClient(AbstractHTTPClient):
    def __init__(self, config: ClouderaSRConfig, *, save_replay: bool = False) -> None:
        s = requests.Session()
        if config.sasl_username is not None:
            s.auth = HTTPKerberosAuth(
                principal=config.sasl_username,
                mutual_authentication=config.mutual_auth,
            )
        if config.ssl_ca_location is not None:
            s.verify = config.ssl_ca_location
        accept = ', '.join([
            'application/vnd.schemaregistry.v1+json',
            'application/vnd.schemaregistry+json',
            'application/json',
        ])
        s.headers.update({
            'Accept': accept,
            'Content-Type': "application/vnd.schemaregistry.v1+json",
        })

        self._session = s
        self._base_url = config.url

        self._save_replay = save_replay

    # ToDo (tribunsky.kir): make method enum
    def make_request(self, relative_url: str, method: str = 'GET', body: Any = None, query: Any = None) -> Any:
        url = "/".join([self._base_url, relative_url.lstrip('/')])
        logger.debug('{0}: {1}'.format(method, url))
        response = self._session.request(method, url, json=body, params=query)
        response.raise_for_status()

        self._dump(method, relative_url, response)
        return response.json()

    def _dump(self, method: str, relative_url: str, response: requests.Response) -> None:
        if self._save_replay:
            filename = '{0}/{1}.json'.format(method, relative_url)
            dir_name = os.path.dirname(filename)
            os.makedirs(dir_name, exist_ok=True)
            with open(filename, 'w') as fl:
                json.dump(response.json(), fl)
