from wunderkafka import AvroProducer, ProducerConfig, SRConfig, SecurityProtocol

BROKERS_ADDRESSES = 'kafka-broker-01.my_domain.com'
SCHEMA_REGISTRY_URL = 'https://schema-registry.my_domain.com'

value_schema = """
{
   "namespace": "my.test",
   "name": "value",
   "type": "record",
   "fields" : [
     {
       "name" : "name",
       "type" : "string"
     }
   ]
}
"""
key_schema = """
{
   "namespace": "my.test",
   "name": "key",
   "type": "record",
   "fields" : [
     {
       "name" : "name",
       "type" : "string"
     }
   ]
}
"""

if __name__ == '__main__':
    config = ProducerConfig(
        bootstrap_servers=BROKERS_ADDRESSES,
        security_protocol=SecurityProtocol.sasl_ssl,
        sasl_kerberos_kinit_cmd='kinit my_user@my_real.com -k -t my_user.keytab',
        sr=SRConfig(url=SCHEMA_REGISTRY_URL, sasl_username='my_user@my_real.com'),
    )

    topic = 'test_test_test'
    producer = AvroProducer({topic: (value_schema, key_schema)}, config)
    producer.send_message(topic, {"name": "Value"}, {"name": "Key"}, blocking=True)
