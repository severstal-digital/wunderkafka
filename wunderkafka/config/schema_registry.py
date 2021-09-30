from enum import Enum
from typing import Any, Dict, Union, Optional

from pydantic import AnyHttpUrl, BaseSettings


class HTTPKerberosMutualAuth(Enum):
    REQUIRED = 1
    OPTIONAL = 2
    DISABLED = 3


# class HTTPKerberosAuthConfig(BaseSettings):
#     sasl_username: Optional[str]
#     mutual_auth: Optional[HTTPKerberosMutualAuth] = None


def remap_fields(dct: Dict[str, Any]) -> Dict[str, Any]:
    return {f_name.replace('_', '.'): f_value for f_name, f_value in dct.items()}


class SRConfig(BaseSettings):
    url: AnyHttpUrl
    ssl_ca_location: Optional[str] = None
    ssl_key_location: Optional[str] = None
    ssl_certificate_location: Optional[str] = None
    basic_auth_user_info: Optional[str] = None

    def dict(self, **kwargs: Any) -> Dict[str, Optional[Union[str, int]]]:
        dct = super().dict(**kwargs)
        return remap_fields(dct)


class ClouderaSRConfig(SRConfig):
    sasl_username: Optional[str]
    mutual_auth: Optional[HTTPKerberosMutualAuth] = None


# ToDo (tribunsky-kir): maybe, it's better to join configs to something like
# class Config:
#     config: ConsumerConfig
#     sr: Optional[SRConfig]  # in the sake of BytesProducer easy use
