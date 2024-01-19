# ToDo (tribunsky.kir): looks like that idea of dynamic import via imp depending on librdkafka
#                       wasn't the worst idea, cause `if`s causes a lot of static checks problems.
# mypy: disable-error-code="no-redef"

from wunderkafka import librdkafka

from enum import Enum


class BrokerAddressFamily(str, Enum):
    any = 'any'
    v4 = 'v4'
    v6 = 'v6'


class SecurityProtocol(str, Enum):
    plaintext = 'plaintext'
    ssl = 'ssl'
    sasl_plaintext = 'sasl_plaintext'
    sasl_ssl = 'sasl_ssl'


class SslEndpointIdentificationAlgorithm(str, Enum):
    none = 'none'
    https = 'https'


class IsolationLevel(str, Enum):
    read_uncommitted = 'read_uncommitted'
    read_committed = 'read_committed'


class AutoOffsetReset(str, Enum):
    smallest = 'smallest'
    earliest = 'earliest'
    beginning = 'beginning'
    largest = 'largest'
    latest = 'latest'
    end = 'end'
    error = 'error'


class CompressionCodec(str, Enum):
    none = 'none'
    gzip = 'gzip'
    snappy = 'snappy'
    lz4 = 'lz4'
    zstd = 'zstd'


class CompressionType(str, Enum):
    none = 'none'
    gzip = 'gzip'
    snappy = 'snappy'
    lz4 = 'lz4'
    zstd = 'zstd'


class QueuingStrategy(str, Enum):
    fifo = 'fifo'
    lifo = 'lifo'

if librdkafka.__version__ >= (1, 5, 0):
    from enum import Enum


    class BrokerAddressFamily(str, Enum):
        any = 'any'
        v4 = 'v4'
        v6 = 'v6'


    class SecurityProtocol(str, Enum):
        plaintext = 'plaintext'
        ssl = 'ssl'
        sasl_plaintext = 'sasl_plaintext'
        sasl_ssl = 'sasl_ssl'


    class SslEndpointIdentificationAlgorithm(str, Enum):
        none = 'none'
        https = 'https'


    class IsolationLevel(str, Enum):
        read_uncommitted = 'read_uncommitted'
        read_committed = 'read_committed'


    class AutoOffsetReset(str, Enum):
        smallest = 'smallest'
        earliest = 'earliest'
        beginning = 'beginning'
        largest = 'largest'
        latest = 'latest'
        end = 'end'
        error = 'error'


    class CompressionCodec(str, Enum):
        none = 'none'
        gzip = 'gzip'
        snappy = 'snappy'
        lz4 = 'lz4'
        zstd = 'zstd'


    class CompressionType(str, Enum):
        none = 'none'
        gzip = 'gzip'
        snappy = 'snappy'
        lz4 = 'lz4'
        zstd = 'zstd'


    class QueuingStrategy(str, Enum):
        fifo = 'fifo'
        lifo = 'lifo'

if librdkafka.__version__ >= (1, 6, 0):
    from enum import Enum


    class BrokerAddressFamily(str, Enum):
        any = 'any'
        v4 = 'v4'
        v6 = 'v6'


    class SecurityProtocol(str, Enum):
        plaintext = 'plaintext'
        ssl = 'ssl'
        sasl_plaintext = 'sasl_plaintext'
        sasl_ssl = 'sasl_ssl'


    class SslEndpointIdentificationAlgorithm(str, Enum):
        none = 'none'
        https = 'https'


    class IsolationLevel(str, Enum):
        read_uncommitted = 'read_uncommitted'
        read_committed = 'read_committed'


    class AutoOffsetReset(str, Enum):
        smallest = 'smallest'
        earliest = 'earliest'
        beginning = 'beginning'
        largest = 'largest'
        latest = 'latest'
        end = 'end'
        error = 'error'


    class CompressionCodec(str, Enum):
        none = 'none'
        gzip = 'gzip'
        snappy = 'snappy'
        lz4 = 'lz4'
        zstd = 'zstd'


    class CompressionType(str, Enum):
        none = 'none'
        gzip = 'gzip'
        snappy = 'snappy'
        lz4 = 'lz4'
        zstd = 'zstd'


    class QueuingStrategy(str, Enum):
        fifo = 'fifo'
        lifo = 'lifo'

if librdkafka.__version__ >= (1, 7, 0):
    from enum import Enum


    class BrokerAddressFamily(str, Enum):
        any = 'any'
        v4 = 'v4'
        v6 = 'v6'


    class SecurityProtocol(str, Enum):
        plaintext = 'plaintext'
        ssl = 'ssl'
        sasl_plaintext = 'sasl_plaintext'
        sasl_ssl = 'sasl_ssl'


    class SslEndpointIdentificationAlgorithm(str, Enum):
        none = 'none'
        https = 'https'


    class IsolationLevel(str, Enum):
        read_uncommitted = 'read_uncommitted'
        read_committed = 'read_committed'


    class AutoOffsetReset(str, Enum):
        smallest = 'smallest'
        earliest = 'earliest'
        beginning = 'beginning'
        largest = 'largest'
        latest = 'latest'
        end = 'end'
        error = 'error'


    class CompressionCodec(str, Enum):
        none = 'none'
        gzip = 'gzip'
        snappy = 'snappy'
        lz4 = 'lz4'
        zstd = 'zstd'


    class CompressionType(str, Enum):
        none = 'none'
        gzip = 'gzip'
        snappy = 'snappy'
        lz4 = 'lz4'
        zstd = 'zstd'


    class QueuingStrategy(str, Enum):
        fifo = 'fifo'
        lifo = 'lifo'

if librdkafka.__version__ >= (1, 8, 0):
    from enum import Enum


    class BrokerAddressFamily(str, Enum):
        any = 'any'
        v4 = 'v4'
        v6 = 'v6'


    class SecurityProtocol(str, Enum):
        plaintext = 'plaintext'
        ssl = 'ssl'
        sasl_plaintext = 'sasl_plaintext'
        sasl_ssl = 'sasl_ssl'


    class SslEndpointIdentificationAlgorithm(str, Enum):
        none = 'none'
        https = 'https'


    class IsolationLevel(str, Enum):
        read_uncommitted = 'read_uncommitted'
        read_committed = 'read_committed'


    class AutoOffsetReset(str, Enum):
        smallest = 'smallest'
        earliest = 'earliest'
        beginning = 'beginning'
        largest = 'largest'
        latest = 'latest'
        end = 'end'
        error = 'error'


    class CompressionCodec(str, Enum):
        none = 'none'
        gzip = 'gzip'
        snappy = 'snappy'
        lz4 = 'lz4'
        zstd = 'zstd'


    class CompressionType(str, Enum):
        none = 'none'
        gzip = 'gzip'
        snappy = 'snappy'
        lz4 = 'lz4'
        zstd = 'zstd'


    class QueuingStrategy(str, Enum):
        fifo = 'fifo'
        lifo = 'lifo'

if librdkafka.__version__ >= (1, 9, 0):
    from enum import Enum


    class BrokerAddressFamily(str, Enum):
        any = 'any'
        v4 = 'v4'
        v6 = 'v6'


    class SecurityProtocol(str, Enum):
        plaintext = 'plaintext'
        ssl = 'ssl'
        sasl_plaintext = 'sasl_plaintext'
        sasl_ssl = 'sasl_ssl'


    class SslEndpointIdentificationAlgorithm(str, Enum):
        none = 'none'
        https = 'https'


    class SaslOauthbearerMethod(str, Enum):
        default = 'default'
        oidc = 'oidc'


    class IsolationLevel(str, Enum):
        read_uncommitted = 'read_uncommitted'
        read_committed = 'read_committed'


    class AutoOffsetReset(str, Enum):
        smallest = 'smallest'
        earliest = 'earliest'
        beginning = 'beginning'
        largest = 'largest'
        latest = 'latest'
        end = 'end'
        error = 'error'


    class CompressionCodec(str, Enum):
        none = 'none'
        gzip = 'gzip'
        snappy = 'snappy'
        lz4 = 'lz4'
        zstd = 'zstd'


    class CompressionType(str, Enum):
        none = 'none'
        gzip = 'gzip'
        snappy = 'snappy'
        lz4 = 'lz4'
        zstd = 'zstd'


    class QueuingStrategy(str, Enum):
        fifo = 'fifo'
        lifo = 'lifo'

if librdkafka.__version__ >= (2, 0, 0):
    from enum import Enum


    class BrokerAddressFamily(str, Enum):
        any = 'any'
        v4 = 'v4'
        v6 = 'v6'


    class SecurityProtocol(str, Enum):
        plaintext = 'plaintext'
        ssl = 'ssl'
        sasl_plaintext = 'sasl_plaintext'
        sasl_ssl = 'sasl_ssl'


    class SslEndpointIdentificationAlgorithm(str, Enum):
        none = 'none'
        https = 'https'


    class SaslOauthbearerMethod(str, Enum):
        default = 'default'
        oidc = 'oidc'


    class IsolationLevel(str, Enum):
        read_uncommitted = 'read_uncommitted'
        read_committed = 'read_committed'


    class AutoOffsetReset(str, Enum):
        smallest = 'smallest'
        earliest = 'earliest'
        beginning = 'beginning'
        largest = 'largest'
        latest = 'latest'
        end = 'end'
        error = 'error'


    class CompressionCodec(str, Enum):
        none = 'none'
        gzip = 'gzip'
        snappy = 'snappy'
        lz4 = 'lz4'
        zstd = 'zstd'


    class CompressionType(str, Enum):
        none = 'none'
        gzip = 'gzip'
        snappy = 'snappy'
        lz4 = 'lz4'
        zstd = 'zstd'


    class QueuingStrategy(str, Enum):
        fifo = 'fifo'
        lifo = 'lifo'

if librdkafka.__version__ >= (2, 1, 0):
    from enum import Enum


    class BrokerAddressFamily(str, Enum):
        any = 'any'
        v4 = 'v4'
        v6 = 'v6'


    class SecurityProtocol(str, Enum):
        plaintext = 'plaintext'
        ssl = 'ssl'
        sasl_plaintext = 'sasl_plaintext'
        sasl_ssl = 'sasl_ssl'


    class SslEndpointIdentificationAlgorithm(str, Enum):
        none = 'none'
        https = 'https'


    class SaslOauthbearerMethod(str, Enum):
        default = 'default'
        oidc = 'oidc'


    class IsolationLevel(str, Enum):
        read_uncommitted = 'read_uncommitted'
        read_committed = 'read_committed'


    class AutoOffsetReset(str, Enum):
        smallest = 'smallest'
        earliest = 'earliest'
        beginning = 'beginning'
        largest = 'largest'
        latest = 'latest'
        end = 'end'
        error = 'error'


    class CompressionCodec(str, Enum):
        none = 'none'
        gzip = 'gzip'
        snappy = 'snappy'
        lz4 = 'lz4'
        zstd = 'zstd'


    class CompressionType(str, Enum):
        none = 'none'
        gzip = 'gzip'
        snappy = 'snappy'
        lz4 = 'lz4'
        zstd = 'zstd'


    class QueuingStrategy(str, Enum):
        fifo = 'fifo'
        lifo = 'lifo'

if librdkafka.__version__ >= (2, 2, 0):
    from enum import Enum


    class BrokerAddressFamily(str, Enum):
        any = 'any'
        v4 = 'v4'
        v6 = 'v6'


    class SecurityProtocol(str, Enum):
        plaintext = 'plaintext'
        ssl = 'ssl'
        sasl_plaintext = 'sasl_plaintext'
        sasl_ssl = 'sasl_ssl'


    class SslEndpointIdentificationAlgorithm(str, Enum):
        none = 'none'
        https = 'https'


    class SaslOauthbearerMethod(str, Enum):
        default = 'default'
        oidc = 'oidc'


    class ClientDnsLookup(str, Enum):
        use_all_dns_ips = 'use_all_dns_ips'
        resolve_canonical_bootstrap_servers_only = 'resolve_canonical_bootstrap_servers_only'


    class IsolationLevel(str, Enum):
        read_uncommitted = 'read_uncommitted'
        read_committed = 'read_committed'


    class AutoOffsetReset(str, Enum):
        smallest = 'smallest'
        earliest = 'earliest'
        beginning = 'beginning'
        largest = 'largest'
        latest = 'latest'
        end = 'end'
        error = 'error'


    class CompressionCodec(str, Enum):
        none = 'none'
        gzip = 'gzip'
        snappy = 'snappy'
        lz4 = 'lz4'
        zstd = 'zstd'


    class CompressionType(str, Enum):
        none = 'none'
        gzip = 'gzip'
        snappy = 'snappy'
        lz4 = 'lz4'
        zstd = 'zstd'


    class QueuingStrategy(str, Enum):
        fifo = 'fifo'
        lifo = 'lifo'

