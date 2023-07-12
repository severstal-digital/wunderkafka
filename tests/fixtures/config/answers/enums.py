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
