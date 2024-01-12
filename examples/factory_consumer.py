from typing import Optional

from wunderkafka.serdes.headers import ConfluentClouderaHeadersHandler
from wunderkafka.consumers.bytes import BytesConsumer
from wunderkafka.schema_registry import ClouderaSRClient
from wunderkafka.hotfixes.watchdog import check_watchdog
from wunderkafka.consumers.constructor import HighLevelDeserializingConsumer
from wunderkafka.schema_registry.cache import SimpleCache
from wunderkafka.schema_registry.transport import KerberizableHTTPClient
from wunderkafka.serdes.avro.deserializers import FastAvroDeserializer


def MyAvroConsumer(
    config: Optional[OverridenConfig] = None,
) -> HighLevelDeserializingConsumer:
    config = config or OverridenConfig()
    config, watchdog = check_watchdog(config)
    return HighLevelDeserializingConsumer(
        consumer=BytesConsumer(config, watchdog),
        schema_registry=ClouderaSRClient(KerberizableHTTPClient(config.sr), SimpleCache()),
        headers_handler=ConfluentClouderaHeadersHandler().parse,
        deserializer=FastAvroDeserializer(),
    )
