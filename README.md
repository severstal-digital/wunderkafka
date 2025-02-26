<img src="./.github/assets/todo-count-badge.svg"> 

# Wunderkafka

>The power of librdkafka for <s>humans</s> pythons

Wunderkafka provides a handful of facades for C-powered consumer/producer. It's built on top of the [confluent-kafka](https://pypi.org/project/confluent-kafka/)

For a quick view on what is going on, please check [Quickstart](https://severstal-digital.github.io/wunderkafka/pages/quickstart/) and [Documentation](https://severstal-digital.github.io/wunderkafka/)

Installation process described [here](https://severstal-digital.github.io/wunderkafka/pages/install/)

## Features

### #TypeSafe librdkafka config

Instead of passing just a `dict` to consumer/producer config, the [pydantic-powered](https://github.com/marcosschroh/dataclasses-avroschema) config is used. 
It is extracted directly from librdkafka's [CONFIGURATION.md](https://github.com/confluentinc/librdkafka/blob/master/CONFIGURATION.md) with some rough parsing.

### Confluent & Cloudera Schema Registry support

Confluent is used as-is, but hortonworks/cloudera schema registry client and (de)serialization protocol are implemented as well (no "admin" methods support).

### Building Kit

Wunderkafka allows you to relatively simply build your own transport for message (de)serialization and eliminate boilerplates for typical cases.

#### Pre-defined config models
```python
import os
from functools import partial

from pydantic import field_validator, Field
from wunderkafka.time import now
from wunderkafka import SRConfig, ConsumerConfig, SecurityProtocol, AvroConsumer


# If you are a fan of 12 factors, you may want to config via env variables
class OverridenSRConfig(SRConfig):
    url: str = Field(alias='SCHEMA_REGISTRY_URL')

    @field_validator('sasl_username')
    @classmethod
    def from_env(cls, v) -> str:
        # And to use 'native' kerberos envs
        return '{0}@{1}'.format(os.environ.get('KRB5_USER'), os.environ.get('KRB5_REALM'))


# Or you want to override some defaults by default (pun intended)
class OverridenConfig(ConsumerConfig):
    # Consumer which do not commit messages automatically
    enable_auto_commit: bool = False
    # And knows nothing after restart due to new gid.
    group_id: str = 'wunderkafka-{0}'.format(now())
    # More 12 factors
    bootstrap_servers: str = Field(env='BOOTSTRAP_SERVER')
    security_protocol: SecurityProtocol = SecurityProtocol.sasl_ssl
    sasl_kerberos_kinit_cmd: str = ''
    sr: SRConfig = OverridenSRConfig()

    @field_validator('sasl_kerberos_kinit_cmd')
    @classmethod
    def format_keytab(cls, v) -> str:
        if not v:
            return 'kinit {0}@{1} -k -t {0}.keytab'.format(os.environ.get('KRB5_USER'), os.environ.get('KRB5_REALM'))
        # Still allowing to set it manually
        return str(v)


# After this, you can `partial` your own Producer/Consumer, something like...
MyConsumer = partial(AvroConsumer, config=OverridenConfig())
# OR
class MyConsumer(AvroConsumer):
    def __init__(self, config: ConsumerConfig = OverridenConfig()):
        super().__init__(config)
```
#### Building your own transport

```python
from typing import Optional

from pydantic import Field

from wunderkafka.config.generated import enums
from wunderkafka.consumers.bytes import BytesConsumer
from wunderkafka.schema_registry import ClouderaSRClient
from wunderkafka.serdes.headers import ConfluentClouderaHeadersHandler
from wunderkafka.consumers.constructor import HighLevelDeserializingConsumer
from wunderkafka.schema_registry.cache import SimpleCache
from wunderkafka.schema_registry.transport import KerberizableHTTPClient
from wunderkafka.serdes.avro.deserializers import FastAvroDeserializer
from wunderkafka import SRConfig, ConsumerConfig, SecurityProtocol


class SRConfig(SRConfig):
    url: str = Field(alias="SCHEMA_REGISTRY_URL")
    security_protocol: SecurityProtocol = SecurityProtocol.sasl_ssl
    sasl_mechanism: str = "SCRAM-SHA-512"
    sasl_username: str = Field(alias="SASL_USERNAME")
    sasl_password: str = Field(alias="SASL_PASSWORD")


class OverridenConsumerConfig(ConsumerConfig):
    enable_auto_commit: bool = False
    auto_offset_reset: enums.AutoOffsetReset = enums.AutoOffsetReset.earliest
    bootstrap_servers: str = Field(env="BOOTSTRAP_SERVERS")
    security_protocol: SecurityProtocol = SecurityProtocol.sasl_ssl
    sasl_mechanism: str = "SCRAM-SHA-512"
    sasl_username: str = Field(alias="SASL_USERNAME")
    sasl_password: str = Field(alias="SASL_PASSWORD")
    sr: SRConfig = Field(default_factory=SRConfig)


# Pydantic/FastAPI style, but you can inherit from `HighLevelDeserializingConsumer` directly
def MyAvroConsumer(
    config: Optional[ConsumerConfig] = None,
) -> HighLevelDeserializingConsumer:
    config = config or OverridenConsumerConfig()
    return HighLevelDeserializingConsumer(
        consumer=BytesConsumer(config),
        schema_registry=ClouderaSRClient(KerberizableHTTPClient(config.sr), SimpleCache()),
        headers_handler=ConfluentClouderaHeadersHandler().parse,
        deserializer=FastAvroDeserializer(),
    )
```

### Avro on-the-fly schema derivation

Supports `dataclasses` and `pydantic.BaseModel` for avro serialization powered by [dataclasses-avroschema](https://github.com/marcosschroh/dataclasses-avroschema) and some rough "metaprogramming":
```python
# dataclass to AVRO schema example
from dataclasses import dataclass
from dataclasses_avroschema import AvroModel

@dataclass
class SomeData(AvroModel):
    field1: int
    field2: str
```
for a topic `topic_name` will become
```json
{
      "type": "record",
      "name": "topic_name_value",
      "fields": [
          {
              "name": "field1",
              "type": "long"
          },
          {
              "name": "field2",
              "type": "string"
          }
      ]
  }
```
and
```python
# pydantic.BaseModel to AVRO schema example

from typing import Optional
from pydantic import BaseModel 

class Event(BaseModel):
  id: Optional[int]
  ts: Optional[int] = None

  class Meta:
      namespace = "any.data"
```
for a topic `topic_name` will become
```json
{
      "type": "record",
      "name": "topic_name_value",
      "namespace": "any.data",
      "fields": [
          {
              "type": ["long", "null"],
              "name": "id"
          },
          {
              "type": ["null", "long"],
              "name": "ts",
              "default": null
          }
      ]
  }
```
