from enum import Enum
from requests.auth import AuthBase

try:
    import requests_kerberos
    from requests_kerberos import HTTPKerberosAuth
except ImportError as exc:
    HAS_KERBEROS = False
else:
    HAS_KERBEROS = True

if HAS_KERBEROS:
    class HTTPKerberosMutualAuth(Enum):
        REQUIRED = requests_kerberos.REQUIRED
        OPTIONAL = requests_kerberos.OPTIONAL
        DISABLED = requests_kerberos.DISABLED

else:
    class HTTPKerberosMutualAuth(Enum):
        REQUIRED = 1
        OPTIONAL = 2
        DISABLED = 3

    class HTTPKerberosAuth(AuthBase):
        def __init__(self, *args, **kwargs) -> None:
            raise exc
