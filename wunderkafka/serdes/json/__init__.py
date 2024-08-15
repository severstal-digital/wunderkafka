HAS_JSON_SCHEMA = True

try:
    from confluent_kafka.schema_registry.json_schema import JSONDeserializer

    __all__ = ["JSONDeserializer", ]
except ImportError:
    HAS_JSON_SCHEMA = False
