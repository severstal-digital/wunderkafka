import os
import json
import subprocess
from typing import Any, Optional

import requests

from wunderkafka.logger import logger
from wunderkafka.schema_registry.abc import AbstractHTTPClient
from wunderkafka.config.schema_registry import SRConfig
from wunderkafka.config.krb.schema_registry import HTTPKerberosAuth


def _single_check_krb(refresh_cmd: str) -> None:
    try:
        subprocess.run(refresh_cmd, timeout=60, stdout=subprocess.PIPE, check=True)
    # Will retry shortly
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        logger.error(exc)
        logger.warning("Krb not refreshed!")


class KerberizableHTTPClient(AbstractHTTPClient):
    def __init__(
        self,
        config: SRConfig,
        *,
        requires_kerberos: bool = False,
        cmd_kerberos: Optional[str] = None,
        save_replay: bool = False,
    ) -> None:
        s = requests.Session()
        if requires_kerberos:
            # In case you haven't updated the krb token
            # but have already gone to SR and you have a krb requirement,
            # do a one-time update
            if cmd_kerberos:
                _single_check_krb(cmd_kerberos)
            else:
                logger.warning(
                    "Before using SR, there was no forced krb authentication! "
                    "Because the `cmd_kerberos` attribute was not passed on"
                )
            s.auth = HTTPKerberosAuth(
                principal=config.sasl_username,
                mutual_authentication=config.mutual_auth,
            )

        if config.ssl_certificate_location is not None:
            if config.ssl_key_location is not None:
                s.cert = (config.ssl_certificate_location, config.ssl_key_location)
            else:
                s.cert = config.ssl_certificate_location

        if config.ssl_key_location is not None:
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
        if response.status_code >= 400:
            # more informative message when fail
            logger.debug("====HTTPError====\n"
                         f"URL: {url}\n"
                         f"Content: {response.content}\n"
                         f"Query: {query}\n"
                         f"Body: {body}\n"
                         "=" * 20 + "\n"
                         )

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
