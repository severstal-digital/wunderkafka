from wunderkafka import AvroConsumer, ConsumerConfig, SRConfig, SecurityProtocol

BROKERS_ADDRESSES = 'kafka-broker-01.my_domain.com'
SCHEMA_REGISTRY_URL = 'https://schema-registry.my_domain.com'

if __name__ == '__main__':
    config = ConsumerConfig(
        enable_auto_commit=False,
        group_id='my_group',
        bootstrap_servers=BROKERS_ADDRESSES,
        security_protocol=SecurityProtocol.sasl_ssl,
        sasl_kerberos_kinit_cmd='kinit my_user@my_real.com -k -t my_user.keytab',
        sr=SRConfig(url=SCHEMA_REGISTRY_URL, sasl_username='my_user@my_real.com'),
    )

    c = AvroConsumer(config)
    c.subscribe(['my_topic'], from_beginning=True)

    while True:
        msgs = c.consume(timeout=10.0, ignore_keys=True)
        print(len(msgs))
