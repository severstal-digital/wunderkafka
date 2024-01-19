from confluent_kafka import KafkaError

from wunderkafka.config.generated import enums
from wunderkafka.config.rdkafka import RDKafkaConfig
from wunderkafka.logger import logger


def exclude_gssapi(builtin_features: str) -> str:
    features = [feature.strip() for feature in builtin_features.split(',') if feature.strip() != 'sasl_gssapi']
    return ', '.join(features)


def config_requires_kerberos(config: RDKafkaConfig) -> bool:
    if config.sasl_mechanism.casefold() != 'GSSAPI'.casefold():
        return False
    if config.sasl_kerberos_keytab is None:
        return False
    return config.security_protocol in {enums.SecurityProtocol.sasl_ssl, enums.SecurityProtocol.sasl_plaintext}


def challenge_krb_arg(exc: KafkaError, config: RDKafkaConfig) -> RDKafkaConfig:
    """
    Check if we can just skip kerberos configuration which comes to RDKafkaConfig from documentation default.

    Currently, I didn't find anything in confluent-kafka to query `builtin.features` from python,
    so we are just checking error while instantiating original consumer/producer
    and override corresponding config values.
    """
    logger.warning('Error while instantiating consumer/producer. Checking builtin.features...')
    # https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#kafkaexception
    error = exc.args[0]
    if error.code() != KafkaError._INVALID_ARG:
        raise
    if 'sasl_gssapi' not in error.str():
        raise
    if config_requires_kerberos(config):
        raise
    else:
        logger.warning(' '.join([
            "Looks like that current client configuration doesn't require kerberos.",
            "As it is not supported by currently installed build, skipping this option.",
        ]))
        old = config.builtin_features
        new = exclude_gssapi(config.builtin_features)
        logger.warning('Changing builtin.features: {0} -> {1}'.format(old, new))
        config.builtin_features = new
        return config
