import datetime

from wunderkafka import BytesConsumer, ConsumerConfig, SecurityProtocol

if __name__ == '__main__':
    # Config is still pretty long, it is an essential complexity.
    # But in minimal setup you only need to specify just `group_id`
    # and `bootstrap_servers`
    config = ConsumerConfig(
        enable_auto_commit=False,
        group_id='my_group',
        bootstrap_servers='kafka-broker-01.my_domain.com:9093',
        security_protocol=SecurityProtocol.sasl_ssl,
        sasl_kerberos_kinit_cmd='kinit my_user@my_realm.com -k -t my_user.keytab',
    )

    consumer = BytesConsumer(config)
    # topic subscription by different timelines is now oneliner without
    # much boilerplate.
    consumer.subscribe(['my_topic'], with_timedelta=datetime.timedelta(hours=10))

    while True:
        msgs = consumer.batch_poll()
        print(
            'Consumed: {0}, errors: {1}'.format(
                len(msgs), len([msg for msg in msgs if msg.error()])
            )
        )
