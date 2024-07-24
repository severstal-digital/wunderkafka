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
