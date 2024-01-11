import os
import json
from typing import Any, Optional

import requests

from wunderkafka.config.krb.rdkafka import config_requires_kerberos
from wunderkafka.config.krb.schema_registry import HTTPKerberosAuth
from wunderkafka.config.rdkafka import RDKafkaConfig
from wunderkafka.hotfixes.watchdog import parse_kinit, KrbWatchDog, check_watchdog, get_version
from wunderkafka.logger import logger
from wunderkafka.schema_registry.abc import AbstractHTTPClient
from wunderkafka.config.schema_registry import SRConfig


class KerberizableHTTPClient(AbstractHTTPClient):
    def __init__(
        self,
        config: RDKafkaConfig,
        *,
        save_replay: bool = False,
    ) -> None:
        if config.sr is None:
            raise RuntimeError("You have not initialized the configuration for Schema Registry!")
        s = requests.Session()
        if config_requires_kerberos(config) and config.sasl_kerberos_kinit_cmd is not None:
            check_watchdog(config)
            s.auth = HTTPKerberosAuth(
                principal=config.sr.sasl_username,
                mutual_authentication=config.sr.mutual_auth,
            )

        if config.sr.ssl_certificate_location is not None:
            if config.sr.ssl_key_location is not None:
                s.cert = (config.sr.ssl_certificate_location, config.ssl_key_location)
            else:
                s.cert = config.sr.ssl_certificate_location

        if config.sr.ssl_key_location is not None:
            s.verify = config.sr.ssl_ca_location

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
        self._base_url = config.sr.url

        self._save_replay = save_replay

    @property
    def base_url(self) -> str:
        return str(self._base_url)

    def close(self) -> None:
        self._session.close()

    # ToDo (tribunsky.kir): make method enum
    def make_request(
        self,
        relative_url: str,
        method: str = 'GET',
        body: Any = None,
        query: Any = None,
    ) -> Any:
        url = "/".join([self._base_url.rstrip('/'), relative_url.lstrip('/')])
        logger.debug('{0}: {1}'.format(method, url))
        response = self._session.request(method, url, json=body, params=query)
        # ToDo(aa.perelygin): more informative message when fail
        if response.status_code >= 400:
            logger.error(f'HTTPError for url: {url}, more details: {response.content}')

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
