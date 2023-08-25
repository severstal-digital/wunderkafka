from typing import Any, Dict, Union, Optional

from pydantic_settings import BaseSettings

from wunderkafka.config.krb.schema_registry import HTTPKerberosMutualAuth


def remap_fields(dct: Dict[str, Any]) -> Dict[str, Any]:
    return {f_name.replace('_', '.'): f_value for f_name, f_value in dct.items()}


class SRConfig(BaseSettings):
    url: str
    ssl_ca_location: Optional[str] = None
    ssl_key_location: Optional[str] = None
    ssl_certificate_location: Optional[str] = None
    basic_auth_user_info: Optional[str] = None

    # ToDo (tribunsky-kir): looks like sasl_username and kerberos over HTTP are cloudera-specific.
    sasl_username: Optional[str] = None
    # ToDo: (tribunsky-kir): I'd prefer to compose the whole HTTP Kerberos stuff as separate subconfig,
    #                        but it entails writing additional logic for sasl username reuse.
    mutual_auth: Optional[HTTPKerberosMutualAuth] = None

    def dict(self, **kwargs: Any) -> Dict[str, Optional[Union[str, int]]]:
        dct = super().model_dump(**kwargs)
        return remap_fields(dct)
