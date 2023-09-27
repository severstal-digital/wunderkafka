from enum import Enum
from typing import Any

from requests.auth import AuthBase

try:
    import requests_kerberos
    from requests_kerberos import HTTPKerberosAuth
except ImportError:
    HAS_KERBEROS = False
else:
    HAS_KERBEROS = True

if HAS_KERBEROS:
    class HTTPKerberosMutualAuth(Enum):
        REQUIRED = requests_kerberos.REQUIRED
        OPTIONAL = requests_kerberos.OPTIONAL
        DISABLED = requests_kerberos.DISABLED

else:
    class HTTPKerberosMutualAuth(Enum):                                                                   # type: ignore
        REQUIRED = 1
        OPTIONAL = 2
        DISABLED = 3

    class HTTPKerberosAuth(AuthBase):                                                                     # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            message = ' '.join([
                'Something went wrong: trying to use HTTPKerberosAuth while missing requests-kerberos.',
                'Maybe it is unexpected manual usage. Please, install requests-kerberos.'
            ])
            raise ImportError(message)
