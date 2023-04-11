import struct
from types import MappingProxyType

from wunderkafka.errors import DeserializerException
from wunderkafka.serdes.abc import AbstractProtocolHandler
from wunderkafka.structures import SRMeta, ParsedHeader
from wunderkafka.serdes.avro.structures import Mask, Protocol

# see: https://git.io/JvYyC
PROTOCOLS = MappingProxyType({
    # public static final byte CONFLUENT_VERSION_PROTOCOL = 0x0;
    0: Protocol(4, Mask('I')),
    # public static final byte METADATA_ID_VERSION_PROTOCOL = 0x1;
    1: Protocol(12, Mask('qi')),
    # public static final byte VERSION_ID_AS_LONG_PROTOCOL = 0x2;
    2: Protocol(8, Mask('q')),
    # public static final byte VERSION_ID_AS_INT_PROTOCOL = 0x3;
    3: Protocol(4, Mask('I')),
})

MIN_HEADER_SIZE = min([pr.header_size for pr in PROTOCOLS.values()]) + 1


class ConfluentClouderaHeadersHandler(AbstractProtocolHandler):

    def parse(self, blob: bytes) -> ParsedHeader:
        if len(blob) < MIN_HEADER_SIZE:
            raise DeserializerException("Message is too small to decode: ({!r})".format(blob))

        # 1st byte is magic byte.
        [protocol_id] = struct.unpack('>b', blob[0:1])

        protocol = PROTOCOLS.get(protocol_id)
        if protocol is None:
            raise DeserializerException('Unknown protocol extracted from message: {0}'.format(protocol_id))

        # already read 1 byte from header as protocol id
        meta = struct.unpack(protocol.mask.unpack, blob[1:1+protocol.header_size])

        if protocol_id == 1:
            schema_id = None
            schema_meta_id, schema_version = meta
        else:
            [schema_id] = meta
            schema_meta_id = None
            schema_version = None

        return ParsedHeader(
            protocol_id=protocol_id,
            meta_id=schema_meta_id,
            schema_id=schema_id,
            schema_version=schema_version,
            size=protocol.header_size + 1,
        )

    def pack(self, protocol_id: int, meta: SRMeta) -> bytes:
        protocol = PROTOCOLS.get(protocol_id)
        if protocol is None:
            raise ValueError('Unknown protocol_id {0}!'.format(protocol_id))

        if protocol_id == 1:
            if meta.meta_id is None:
                err_msg = 'No meta id for protocol_id {0}. Please, check response from Schema Registry.'.format(
                    protocol_id)
                raise ValueError(err_msg)
            return struct.pack(protocol.mask.pack, protocol_id, meta.meta_id, meta.schema_version)
        else:
            return struct.pack(protocol.mask.pack, protocol_id, meta.schema_id)
