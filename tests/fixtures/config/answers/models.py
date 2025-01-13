######################################################################
########### THIS FILE IS GENERATED, DO NOT EDIT MANUALLY!!! ##########
########### THIS FILE IS GENERATED, DO NOT EDIT MANUALLY!!! ##########
########### THIS FILE IS GENERATED, DO NOT EDIT MANUALLY!!! ##########
########### THIS FILE IS GENERATED, DO NOT EDIT MANUALLY!!! ##########
########### THIS FILE IS GENERATED, DO NOT EDIT MANUALLY!!! ##########
######################################################################

from typing import Callable, Optional

from pydantic import Field
from pydantic_settings import BaseSettings

# Enums because we can't rely that client code uses linters.
# Of course, it will fail with cimpl.KafkaException, but later, when Consumer/Producer are really initiated
from wunderkafka.config.generated import enums


class RDKafkaConfig(BaseSettings):
    api_version_fallback_ms: int = Field(ge=0, le=604800000, default=0)
    api_version_request: bool = True
    api_version_request_timeout_ms: int = Field(ge=1, le=300000, default=10000)
    background_event_cb: Optional[Callable] = None
    bootstrap_servers: Optional[str] = None
    broker_address_family: enums.BrokerAddressFamily = enums.BrokerAddressFamily.any
    broker_address_ttl: int = Field(ge=0, le=86400000, default=1000)
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
    enabled_events: int = Field(ge=0, le=2147483647, default=0)
    error_cb: Optional[Callable] = None
    interceptors: Optional[Callable] = None
    internal_termination_signal: int = Field(ge=0, le=128, default=0)
    log_cb: Optional[Callable] = None
    log_connection_close: bool = True
    log_level: int = Field(ge=0, le=7, default=6)
    log_queue: bool = False
    log_thread_name: bool = True
    max_in_flight: int = Field(ge=1, le=1000000, default=1000000)
    max_in_flight_requests_per_connection: int = Field(ge=1, le=1000000, default=1000000)
    message_copy_max_bytes: int = Field(ge=0, le=1000000000, default=65535)
    message_max_bytes: int = Field(ge=1000, le=1000000000, default=1000000)
    metadata_broker_list: Optional[str] = None
    metadata_max_age_ms: int = Field(ge=1, le=86400000, default=900000)
    metadata_request_timeout_ms: int = Field(ge=10, le=900000, default=60000)
    oauthbearer_token_refresh_cb: Optional[Callable] = None
    opaque: Optional[Callable] = None
    open_cb: Optional[Callable] = None
    plugin_library_paths: Optional[str] = None
    receive_message_max_bytes: int = Field(ge=1000, le=2147483647, default=100000000)
    reconnect_backoff_max_ms: int = Field(ge=0, le=3600000, default=10000)
    reconnect_backoff_ms: int = Field(ge=0, le=3600000, default=100)
    sasl_kerberos_keytab: Optional[str] = None
    sasl_kerberos_kinit_cmd: str = 'kinit -R -t "%{sasl.kerberos.keytab}" -k %{sasl.kerberos.principal} || kinit -t "%{sasl.kerberos.keytab}" -k %{sasl.kerberos.principal}'
    sasl_kerberos_min_time_before_relogin: int = Field(ge=0, le=86400000, default=60000)
    sasl_kerberos_principal: str = 'kafkaclient'
    sasl_kerberos_service_name: str = 'kafka'
    sasl_mechanism: str = 'GSSAPI'
    # ToDo (tribunsky.kir): rethink using aliases? They may need simultaneous valdiation or may be injected via dict()
    # It is just alias, but when setting it manually it may misbehave with current defaults.
    # sasl_mechanisms: str = 'GSSAPI'
    sasl_oauthbearer_config: Optional[str] = None
    sasl_password: Optional[str] = None
    sasl_username: Optional[str] = None
    security_protocol: enums.SecurityProtocol = enums.SecurityProtocol.plaintext
    socket_cb: Optional[Callable] = None
    socket_keepalive_enable: bool = False
    socket_max_fails: int = Field(ge=0, le=1000000, default=1)
    socket_nagle_disable: bool = False
    socket_receive_buffer_bytes: int = Field(ge=0, le=100000000, default=0)
    socket_send_buffer_bytes: int = Field(ge=0, le=100000000, default=0)
    socket_timeout_ms: int = Field(ge=10, le=300000, default=60000)
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
    statistics_interval_ms: int = Field(ge=0, le=86400000, default=0)
    stats_cb: Optional[Callable] = None
    throttle_cb: Optional[Callable] = None
    topic_blacklist: Optional[str] = None
    topic_metadata_propagation_max_ms: int = Field(ge=0, le=3600000, default=30000)
    topic_metadata_refresh_fast_interval_ms: int = Field(ge=1, le=60000, default=250)
    topic_metadata_refresh_interval_ms: int = Field(ge=-1, le=3600000, default=300000)
    topic_metadata_refresh_sparse: bool = True


class RDConsumerConfig(RDKafkaConfig):
    group_id: str
    allow_auto_create_topics: bool = False
    auto_commit_interval_ms: int = Field(ge=0, le=86400000, default=5000)
    auto_offset_reset: enums.AutoOffsetReset = enums.AutoOffsetReset.largest
    check_crcs: bool = False
    consume_callback_max_messages: int = Field(ge=0, le=1000000, default=0)
    consume_cb: Optional[Callable] = None
    coordinator_query_interval_ms: int = Field(ge=1, le=3600000, default=600000)
    enable_auto_commit: bool = True
    enable_auto_offset_store: bool = True
    enable_partition_eof: bool = False
    fetch_error_backoff_ms: int = Field(ge=0, le=300000, default=500)
    fetch_max_bytes: int = Field(ge=0, le=2147483135, default=52428800)
    fetch_message_max_bytes: int = Field(ge=1, le=1000000000, default=1048576)
    fetch_min_bytes: int = Field(ge=1, le=100000000, default=1)
    fetch_wait_max_ms: int = Field(ge=0, le=300000, default=500)
    group_instance_id: Optional[str] = None
    group_protocol_type: str = 'consumer'
    heartbeat_interval_ms: int = Field(ge=1, le=3600000, default=3000)
    isolation_level: enums.IsolationLevel = enums.IsolationLevel.read_committed
    max_partition_fetch_bytes: int = Field(ge=1, le=1000000000, default=1048576)
    max_poll_interval_ms: int = Field(ge=1, le=86400000, default=300000)
    offset_commit_cb: Optional[Callable] = None
    partition_assignment_strategy: str = 'range,roundrobin'
    queued_max_messages_kbytes: int = Field(ge=1, le=2097151, default=65536)
    queued_min_messages: int = Field(ge=1, le=10000000, default=100000)
    rebalance_cb: Optional[Callable] = None
    session_timeout_ms: int = Field(ge=1, le=3600000, default=10000)


class RDProducerConfig(RDKafkaConfig):
    acks: int = Field(ge=-1, le=1000, default=-1)
    batch_num_messages: int = Field(ge=1, le=1000000, default=10000)
    batch_size: int = Field(ge=1, le=2147483647, default=1000000)
    compression_codec: enums.CompressionCodec = enums.CompressionCodec.none
    compression_level: int = Field(ge=-1, le=12, default=-1)
    compression_type: enums.CompressionType = enums.CompressionType.none
    delivery_report_only_error: bool = False
    delivery_timeout_ms: int = Field(ge=0, le=2147483647, default=300000)
    dr_cb: Optional[Callable] = None
    dr_msg_cb: Optional[Callable] = None
    enable_gapless_guarantee: bool = False
    enable_idempotence: bool = False
    linger_ms: float = Field(ge=0, le=900000, default=5.0)
    message_send_max_retries: int = Field(ge=0, le=10000000, default=2)
    message_timeout_ms: int = Field(ge=0, le=2147483647, default=300000)
    msg_order_cmp: Optional[Callable] = None
    partitioner: str = 'consistent_random'
    partitioner_cb: Optional[Callable] = None
    queue_buffering_backpressure_threshold: int = Field(ge=1, le=1000000, default=1)
    queue_buffering_max_kbytes: int = Field(ge=1, le=2147483647, default=1048576)
    queue_buffering_max_messages: int = Field(ge=1, le=10000000, default=100000)
    queue_buffering_max_ms: float = Field(ge=0, le=900000, default=5.0)
    queuing_strategy: enums.QueuingStrategy = enums.QueuingStrategy.fifo
    request_required_acks: int = Field(ge=-1, le=1000, default=-1)
    request_timeout_ms: int = Field(ge=1, le=900000, default=5000)
    retries: int = Field(ge=0, le=10000000, default=2)
    retry_backoff_ms: int = Field(ge=1, le=300000, default=100)
    transaction_timeout_ms: int = Field(ge=1000, le=2147483647, default=60000)
    transactional_id: Optional[str] = None
