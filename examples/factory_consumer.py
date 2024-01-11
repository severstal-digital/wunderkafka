from typing import Optional

from wunderkafka.config.krb.rdkafka import config_requires_kerberos
from wunderkafka.consumers.bytes import BytesConsumer
from wunderkafka.consumers.constructor import HighLevelDeserializingConsumer
from wunderkafka.hotfixes.watchdog import check_watchdog
from wunderkafka.schema_registry.cache import SimpleCache
from wunderkafka.schema_registry.client import ClouderaSRClient
from wunderkafka.schema_registry.transport import KerberizableHTTPClient
from wunderkafka.serdes.avro.deserializers import FastAvroDeserializer
from wunderkafka.serdes.avro.headers import AvroClouderaConfluent


def MyAvroConsumer(
    config: Optional[OverridenConfig] = None,
) -> HighLevelDeserializingConsumer:
    config = config or OverridenConfig()
    config, watchdog = check_watchdog(config)
    return HighLevelDeserializingConsumer(
        consumer=BytesConsumer(config, watchdog),
        schema_registry=ClouderaSRClient(KerberizableHTTPClient(
            config.sr,
            requires_kerberos=config_requires_kerberos(config)
        ), SimpleCache()),
        headers_handler=AvroClouderaConfluent(),
        deserializer=FastAvroDeserializer(),
    )
