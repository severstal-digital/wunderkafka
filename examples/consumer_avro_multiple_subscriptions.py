import datetime

from wunderkafka import AvroConsumer, ConsumerConfig, SRConfig, SecurityProtocol, TopicSubscription

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
    c.subscribe([
        TopicSubscription('my_topic1', with_timedelta=datetime.timedelta(minutes=10)),
        TopicSubscription('my_topic2', from_beginning=True),
        # Will also work with "default" subscription option
        'my_topic3',
    ])

    while True:
        msgs = c.consume(timeout=10.0, ignore_keys=True)
        print(len(msgs))
