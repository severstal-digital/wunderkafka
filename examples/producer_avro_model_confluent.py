from pydantic import BaseModel, Field
from wunderkafka import ProducerConfig, SRConfig, SecurityProtocol, AvroModelConfluentProducer
from wunderkafka.time import now

BROKERS_ADDRESSES = 'kafka-broker-01.my_domain.com'
SCHEMA_REGISTRY_URL = 'https://schema-registry.my_domain.com'


class SomeEvent(BaseModel):
    name: str = 'test'
    ts: int = Field(default_factory=now)


if __name__ == '__main__':
    config = ProducerConfig(
        bootstrap_servers=BROKERS_ADDRESSES,
        security_protocol=SecurityProtocol.sasl_ssl,
        sasl_kerberos_kinit_cmd='kinit my_user@my_real.com -k -t my_user.keytab',
        sr=SRConfig(url=SCHEMA_REGISTRY_URL, sasl_username='my_user@my_real.com'),
    )

    topic = 'test_test_test'

    # No key, that's just an example
    producer = AvroModelConfluentProducer(
        {topic: SomeEvent},
        config,
    )
    producer.send_message(topic, SomeEvent(), blocking=True)
