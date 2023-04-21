from enum import Enum

import requests_kerberos


class HTTPKerberosMutualAuth(Enum):
    REQUIRED = requests_kerberos.REQUIRED
    OPTIONAL = requests_kerberos.OPTIONAL
    DISABLED = requests_kerberos.DISABLED
