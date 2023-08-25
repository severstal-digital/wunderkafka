# I am not gonna to generate single type for every single range of conint/confloat.
# https://github.com/samuelcolvin/pydantic/issues/156

from typing import Callable, Optional

from pydantic import conint, confloat
from pydantic_settings import BaseSettings

# Enums because we can't rely that client code uses linters.
# Of course, it will fail with cimpl.KafkaException, but later, when Consumer/Producer are really initiated
from wunderkafka.config.generated import enums


class RDKafkaConfig(BaseSettings):
    api_version_fallback_ms: conint(ge=0, le=604800000) = 0                                   # type: ignore[valid-type]
    api_version_request: bool = True
    api_version_request_timeout_ms: conint(ge=1, le=300000) = 10000                           # type: ignore[valid-type]
    background_event_cb: Optional[Callable] = None
    bootstrap_servers: Optional[str] = None
    broker_address_family: enums.BrokerAddressFamily = enums.BrokerAddressFamily.any
    broker_address_ttl: conint(ge=0, le=86400000) = 1000                                      # type: ignore[valid-type]
    broker_version_fallback: str = '0.10.0'
    builtin_features: str = ', '.join([
        'gzip',
        'snappy',
        'ssl',
        'sasl',
        'regex',
        'lz4',
        'sasl_gssapi',
        'sasl_plain',
        'sasl_scram',
        'plugins',
        'zstd',
        'sasl_oauthbearer',
    ])
    client_id: str = 'rdkafka'
    client_rack: Optional[str] = None
    closesocket_cb: Optional[Callable] = None
    connect_cb: Optional[Callable] = None
    debug: Optional[str] = None
    default_topic_conf: Optional[Callable] = None
    enable_random_seed: bool = True
    enable_sasl_oauthbearer_unsecure_jwt: bool = False
    enable_ssl_certificate_verification: bool = True
    enabled_events: conint(ge=0, le=2147483647) = 0                                           # type: ignore[valid-type]
    error_cb: Optional[Callable] = None
    interceptors: Optional[Callable] = None
    internal_termination_signal: conint(ge=0, le=128) = 0                                     # type: ignore[valid-type]
    log_cb: Optional[Callable] = None
    log_connection_close: bool = True
    log_level: conint(ge=0, le=7) = 6                                                         # type: ignore[valid-type]
    log_queue: bool = False
    log_thread_name: bool = True
    max_in_flight: conint(ge=1, le=1000000) = 1000000                                         # type: ignore[valid-type]
    max_in_flight_requests_per_connection: conint(ge=1, le=1000000) = 1000000                 # type: ignore[valid-type]
    message_copy_max_bytes: conint(ge=0, le=1000000000) = 65535                               # type: ignore[valid-type]
    message_max_bytes: conint(ge=1000, le=1000000000) = 1000000                               # type: ignore[valid-type]
    metadata_broker_list: Optional[str] = None
    metadata_max_age_ms: conint(ge=1, le=86400000) = 900000                                   # type: ignore[valid-type]
    metadata_request_timeout_ms: conint(ge=10, le=900000) = 60000                             # type: ignore[valid-type]
    oauthbearer_token_refresh_cb: Optional[Callable] = None
    opaque: Optional[Callable] = None
    open_cb: Optional[Callable] = None
    plugin_library_paths: Optional[str] = None
    receive_message_max_bytes: conint(ge=1000, le=2147483647) = 100000000                     # type: ignore[valid-type]
    reconnect_backoff_max_ms: conint(ge=0, le=3600000) = 10000                                # type: ignore[valid-type]
    reconnect_backoff_ms: conint(ge=0, le=3600000) = 100                                      # type: ignore[valid-type]
    sasl_kerberos_keytab: Optional[str] = None
    sasl_kerberos_kinit_cmd: str = 'kinit -R -t "%{sasl.kerberos.keytab}" -k %{sasl.kerberos.principal} || kinit -t "%{sasl.kerberos.keytab}" -k %{sasl.kerberos.principal}'
    sasl_kerberos_min_time_before_relogin: conint(ge=0, le=86400000) = 60000                  # type: ignore[valid-type]
    sasl_kerberos_principal: str = 'kafkaclient'
    sasl_kerberos_service_name: str = 'kafka'
    sasl_mechanism: str = 'GSSAPI'
    sasl_mechanisms: str = 'GSSAPI'
    sasl_oauthbearer_config: Optional[str] = None
    sasl_password: Optional[str] = None
    sasl_username: Optional[str] = None
    security_protocol: enums.SecurityProtocol = enums.SecurityProtocol.plaintext
    socket_cb: Optional[Callable] = None
    socket_keepalive_enable: bool = False
    socket_max_fails: conint(ge=0, le=1000000) = 1                                            # type: ignore[valid-type]
    socket_nagle_disable: bool = False
    socket_receive_buffer_bytes: conint(ge=0, le=100000000) = 0                               # type: ignore[valid-type]
    socket_send_buffer_bytes: conint(ge=0, le=100000000) = 0                                  # type: ignore[valid-type]
    socket_timeout_ms: conint(ge=10, le=300000) = 60000                                       # type: ignore[valid-type]
    ssl_ca: Optional[Callable] = None
    ssl_ca_location: Optional[str] = None
    ssl_certificate: Optional[Callable] = None
    ssl_certificate_location: Optional[str] = None
    ssl_certificate_pem: Optional[str] = None
    ssl_certificate_verify_cb: Optional[Callable] = None
    ssl_cipher_suites: Optional[str] = None
    ssl_crl_location: Optional[str] = None
    ssl_curves_list: Optional[str] = None
    ssl_endpoint_identification_algorithm: enums.SslEndpointIdentificationAlgorithm = enums.SslEndpointIdentificationAlgorithm.none
    ssl_key: Optional[Callable] = None
    ssl_key_location: Optional[str] = None
    ssl_key_password: Optional[str] = None
    ssl_key_pem: Optional[str] = None
    ssl_keystore_location: Optional[str] = None
    ssl_keystore_password: Optional[str] = None
    ssl_sigalgs_list: Optional[str] = None
    statistics_interval_ms: conint(ge=0, le=86400000) = 0                                     # type: ignore[valid-type]
    stats_cb: Optional[Callable] = None
    throttle_cb: Optional[Callable] = None
    topic_blacklist: Optional[str] = None
    topic_metadata_propagation_max_ms: conint(ge=0, le=3600000) = 30000                       # type: ignore[valid-type]
    topic_metadata_refresh_fast_interval_ms: conint(ge=1, le=60000) = 250                     # type: ignore[valid-type]
    topic_metadata_refresh_interval_ms: conint(ge=-1, le=3600000) = 300000                    # type: ignore[valid-type]
    topic_metadata_refresh_sparse: bool = True

    @property
    def requires_kerberos(self) -> bool:
        if self.sasl_mechanism != 'GSSAPI':
            return False
        has_credentials = (self.sasl_username is not None and self.sasl_password is not None) or self.sasl_kerberos_keytab is None
        if not has_credentials:
            return False
        return self.security_protocol in {enums.SecurityProtocol.sasl_ssl, enums.SecurityProtocol.sasl_ssl}


class RDConsumerConfig(RDKafkaConfig):
    group_id: str
    allow_auto_create_topics: bool = False
    auto_commit_interval_ms: conint(ge=0, le=86400000) = 5000                                 # type: ignore[valid-type]
    auto_offset_reset: enums.AutoOffsetReset = enums.AutoOffsetReset.largest
    check_crcs: bool = False
    consume_callback_max_messages: conint(ge=0, le=1000000) = 0                               # type: ignore[valid-type]
    consume_cb: Optional[Callable] = None
    coordinator_query_interval_ms: conint(ge=1, le=3600000) = 600000                          # type: ignore[valid-type]
    enable_auto_commit: bool = True
    enable_auto_offset_store: bool = True
    enable_partition_eof: bool = False
    fetch_error_backoff_ms: conint(ge=0, le=300000) = 500                                     # type: ignore[valid-type]
    fetch_max_bytes: conint(ge=0, le=2147483135) = 52428800                                   # type: ignore[valid-type]
    fetch_message_max_bytes: conint(ge=1, le=1000000000) = 1048576                            # type: ignore[valid-type]
    fetch_min_bytes: conint(ge=1, le=100000000) = 1                                           # type: ignore[valid-type]
    fetch_wait_max_ms: conint(ge=0, le=300000) = 500                                          # type: ignore[valid-type]
    group_instance_id: Optional[str] = None
    group_protocol_type: str = 'consumer'
    heartbeat_interval_ms: conint(ge=1, le=3600000) = 3000                                    # type: ignore[valid-type]
    isolation_level: enums.IsolationLevel = enums.IsolationLevel.read_committed
    max_partition_fetch_bytes: conint(ge=1, le=1000000000) = 1048576                          # type: ignore[valid-type]
    max_poll_interval_ms: conint(ge=1, le=86400000) = 300000                                  # type: ignore[valid-type]
    offset_commit_cb: Optional[Callable] = None
    partition_assignment_strategy: str = 'range,roundrobin'
    queued_max_messages_kbytes: conint(ge=1, le=2097151) = 65536                              # type: ignore[valid-type]
    queued_min_messages: conint(ge=1, le=10000000) = 100000                                   # type: ignore[valid-type]
    rebalance_cb: Optional[Callable] = None
    session_timeout_ms: conint(ge=1, le=3600000) = 10000                                      # type: ignore[valid-type]


class RDProducerConfig(RDKafkaConfig):
    acks: conint(ge=-1, le=1000) = -1                                                         # type: ignore[valid-type]
    batch_num_messages: conint(ge=1, le=1000000) = 10000                                      # type: ignore[valid-type]
    batch_size: conint(ge=1, le=2147483647) = 1000000                                         # type: ignore[valid-type]
    compression_codec: enums.CompressionCodec = enums.CompressionCodec.none
    compression_level: conint(ge=-1, le=12) = -1                                              # type: ignore[valid-type]
    compression_type: enums.CompressionType = enums.CompressionType.none
    delivery_report_only_error: bool = False
    delivery_timeout_ms: conint(ge=0, le=2147483647) = 300000                                 # type: ignore[valid-type]
    dr_cb: Optional[Callable] = None
    dr_msg_cb: Optional[Callable] = None
    enable_gapless_guarantee: bool = False
    enable_idempotence: bool = False
    linger_ms: confloat(ge=0, le=900000) = 5.0                                                # type: ignore[valid-type]
    message_send_max_retries: conint(ge=0, le=10000000) = 2                                   # type: ignore[valid-type]
    message_timeout_ms: conint(ge=0, le=2147483647) = 300000                                  # type: ignore[valid-type]
    msg_order_cmp: Optional[Callable] = None
    partitioner: str = 'consistent_random'
    partitioner_cb: Optional[Callable] = None
    queue_buffering_backpressure_threshold: conint(ge=1, le=1000000) = 1                      # type: ignore[valid-type]
    queue_buffering_max_kbytes: conint(ge=1, le=2147483647) = 1048576                         # type: ignore[valid-type]
    queue_buffering_max_messages: conint(ge=1, le=10000000) = 100000                          # type: ignore[valid-type]
    queue_buffering_max_ms: confloat(ge=0, le=900000) = 5.0                                   # type: ignore[valid-type]
    queuing_strategy: enums.QueuingStrategy = enums.QueuingStrategy.fifo
    request_required_acks: conint(ge=-1, le=1000) = -1                                        # type: ignore[valid-type]
    request_timeout_ms: conint(ge=1, le=900000) = 5000                                        # type: ignore[valid-type]
    retries: conint(ge=0, le=10000000) = 2                                                    # type: ignore[valid-type]
    retry_backoff_ms: conint(ge=1, le=300000) = 100                                           # type: ignore[valid-type]
    transaction_timeout_ms: conint(ge=1000, le=2147483647) = 60000                            # type: ignore[valid-type]
    transactional_id: Optional[str] = None
