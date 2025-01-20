from typing import Optional

from wunderkafka.consumers.bytes import BytesConsumer
from wunderkafka.schema_registry import ClouderaSRClient
from wunderkafka.serdes.headers import ConfluentClouderaHeadersHandler
from wunderkafka.consumers.constructor import HighLevelDeserializingConsumer
from wunderkafka.schema_registry.cache import SimpleCache
from wunderkafka.schema_registry.transport import KerberizableHTTPClient
from wunderkafka.serdes.avro.deserializers import FastAvroDeserializer


def MyAvroConsumer(
    config: Optional[OverridenConfig] = None,
) -> HighLevelDeserializingConsumer:
    config = config or OverridenConfig()
    return HighLevelDeserializingConsumer(
        consumer=BytesConsumer(config),
        schema_registry=ClouderaSRClient(
            KerberizableHTTPClient(config.sr, krb_timeout=10), 
            SimpleCache()
        ),
        headers_handler=ConfluentClouderaHeadersHandler().parse,
        deserializer=FastAvroDeserializer(),
    )
