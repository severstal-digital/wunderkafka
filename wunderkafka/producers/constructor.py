"""
This module contains the high-level pipeline to produce messages with a nested producer.

It is intended to be testable enough due to the composition of dependencies.

All moving parts should be interchangeable in terms of schema, header and serialization handling
(for further overriding^W extending).
"""

from typing import Any, Dict, Tuple, Optional

from wunderkafka.types import MsgKey, MsgValue, TopicName, HeaderPacker, DeliveryCallback, MessageDescription
from wunderkafka.logger import logger
from wunderkafka.callbacks import error_callback
from wunderkafka.serdes.abc import AbstractSerializer, AbstractDescriptionStore
from wunderkafka.structures import SRMeta, SchemaDescription
from wunderkafka.producers.abc import AbstractProducer, AbstractSerializingProducer
from wunderkafka.schema_registry.abc import AbstractSchemaRegistry


class HighLevelSerializingProducer(AbstractSerializingProducer):
    """Serializing pipeline implementation of extended producer."""

    def __init__(  # noqa: WPS211  # ToDo (tribunsky.kir): rethink building of producer.
        #                                                  Maybe single Callable (like in kafka-python) much better.
        self,
        producer: AbstractProducer,
        # Some serializers doesn't need SR at all, e.g. StringSerializer.
        schema_registry: Optional[AbstractSchemaRegistry],
        # As some serializers doesn't contain magic byte, we do not need to handle the first bytes of a message at all.
        header_packer: Optional[HeaderPacker],
        serializer: Optional[AbstractSerializer] = None,
        store: Optional[AbstractDescriptionStore] = None,
        # ToDo: switch mapping to something like consumer's TopicSubscription?
        mapping: Optional[Dict[TopicName, MessageDescription]] = None,
        value_serializer: Optional[AbstractSerializer] = None,
        key_serializer: Optional[AbstractSerializer] = None,
        *,
        protocol_id: int = 1,
        lazy: bool = False,
    ) -> None:
        """
        Init producer with specific dependencies and prepare it to work against specified topic(s).

        :param producer:            Producer implementation to send messages.
        :param schema_registry:     Schema registry client.
        :param header_packer:       Callable to form binary headers.
        :param serializer:          Common message serializer for the key and value.
                                    If specific value_deserializer/key_deserializer defined, it will be used instead.
        :param store:               Specific store to provide schema text extraction from schema description.
        :param mapping:             Per-topic definition of value and/or key schema descriptions.
        :param value_serializer:    Message serializer for value, if set.
        :param key_serializer:      Message serializer for the key, if set.
        :param protocol_id:         Protocol id for producer (1 - Cloudera, 0 - Confluent, etc.)
        :param lazy:                If True,
                                    defer schema registry publication, otherwise schema will be registered
                                    before the first message sending.
        """
        self._mapping = mapping or {}

        # ToDo (tribunsky.kir): look like wrong place. Maybe it's better to highlight an entity
        #                       of Schema which may be checked or not. Then input mapping may be eliminated (or not).
        self._checked: Dict[Tuple[str, str, bool], SRMeta] = {}

        self._store = store
        self._sr = schema_registry
        self._serializer = serializer
        self._producer = producer
        self._header_packer = header_packer
        self._protocol_id = protocol_id

        chosen_value_serializer = value_serializer if value_serializer else serializer
        if chosen_value_serializer is None:
            msg = 'Value serializer is not specified, should be passed via value_serializer or serializer at least.'
            raise ValueError(msg)
        self._value_serializer = chosen_value_serializer

        chosen_key_serializer = key_serializer if value_serializer else serializer
        if chosen_key_serializer is None:
            msg = 'Key serializer is not specified, should be passed via key_serializer or serializer at least.'
            raise ValueError(msg)
        self._key_serializer = chosen_key_serializer

        for topic, description in self._mapping.items():
            if isinstance(description, (tuple, list)):
                msg_value, msg_key = description
                self.set_target_topic(topic, msg_value, msg_key, lazy=lazy)
            else:
                self.set_target_topic(topic, description, lazy=lazy)

    def flush(self, timeout: Optional[float] = None) -> int:  # noqa: D102 # docstring inherited from superclass.
        if timeout is None:
            return self._producer.flush()
        return self._producer.flush(timeout)

    def set_target_topic(  # noqa: D102 # docstring inherited from superclass.
        self,
        topic: str,
        value: Any,  # noqa: WPS110 # Domain. inherited from superclass.
        key: Any = None,
        *,
        lazy: bool = False,
    ) -> None:
        value_store = self._get_store(self._value_serializer)
        key_store = self._get_store(self._key_serializer)
        value_store.add(topic, value, None)
        if key is not None:
            # FixMe (tribunsky.kir): make key and value stores independent,
            #                        because now we cannot put None instead of value,
            #                        even though we need store only for the key.
            key_store.add(topic, value, key)
        if not lazy:
            value_descr = value_store.get(topic)
            self._check_schema(topic, value_descr)
            if key is not None:
                key_descr = key_store.get(topic, is_key=True)
                assert key_descr is not None
                if not key_descr.empty:
                    self._check_schema(topic, key_descr, is_key=True)

    def send_message(  # noqa: D102,WPS211 # inherited from superclass.
        self,
        topic: str,
        value: MsgValue = None,  # noqa: WPS110 # Domain. inherited from superclass.
        key: MsgKey = None,
        partition: Optional[int] = None,
        on_delivery: Optional[DeliveryCallback] = error_callback,
        *args: Any,
        blocking: bool = False,
        protocol_id: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        if protocol_id is None:
            protocol_id = self._protocol_id
        encoded_value = self._encode(topic, value, protocol_id)
        encoded_key = self._encode(topic, key, protocol_id, is_key=True)

        self._producer.send_message(
            topic,
            encoded_value,
            encoded_key,
            partition,
            on_delivery,
            blocking=blocking,
            *args,
            **kwargs,
        )

    def _check_schema(
        self,
        topic: str,
        schema: Optional[SchemaDescription],
        *,
        is_key: bool = False,
        force: bool = False,
    ) -> Optional[SRMeta]:
        """
        Ensure that we have schema's ids necessary to create message's header.

        :param topic:   Target topic against which we are working for this call.
        :param schema:  Schema container to be registered. Should contain text.
        :param is_key:  If True, schema will be requested as a message key, message value otherwise.
        :param force:   If True, do not reuse cached results, always request Schema Registry.

        :raises ValueError: If received no schema from DescriptionStore.

        :return:        Container with schema's ids.
        """
        if self._sr is None:
            logger.warning('Schema registry is not passed, skipping schema check for {0}'.format(topic))
            return None
        if schema is None:
            raise ValueError("Couldn't check schema from store.")
        uid = (topic, schema.text, is_key)

        if force is False:
            meta = self._checked.get(uid)
            if meta is not None:
                return meta

        assert schema.type is not None
        meta = self._sr.register_schema(topic, schema.text, schema.type, is_key=is_key)
        self._checked[uid] = meta
        return meta

    # ToDo (tribunsky.kir): Maybe, this method should be public for more simple extension.
    #                       'Template' pattern never works anyway.
    def _encode(self, topic: str, obj: Any, protocol_id: int, is_key: bool = False) -> Optional[bytes]:  # noqa: WPS110
        if obj is None:
            return None

        serializer = self._get_serializer(is_key)
        store = self._get_store(serializer)

        schema = store.get(topic, is_key=is_key)
        if schema is None:
            logger.warning('Missing schema for {0} (key: {1}'.format(topic, is_key))
            return None
        if schema.empty:
            return serializer.serialize(schema.text, obj, None, topic, is_key=is_key)
        else:
            available_meta = self._check_schema(topic, schema, is_key=is_key)
            # ToDo (tribunsky.kir): `_check_schema()` for now return Optional cause it is used when setting
            #                       producer per topic and should not push schema to on schemaless serializers.
            assert available_meta is not None
            # ToDo (tribunsky.kir): looks like header handler should be also placed per-payload or per-topic,
            #                       because some serializers doesn't use it (e.g. confluent string serializer)
            assert self._header_packer is not None
            # ToDo (tribunsky.kir): check if old client uses
            #                       '{"schema": "{\"type\": \"string\"}"}'
            #                       https://docs.confluent.io/platform/current/schema-registry/develop/using.html#common-sr-api-usage-examples  # noqa: E501
            #                       Looks like the new one doesn't publish string schema at all
            #                       (no type in library for that)
            header = self._header_packer(protocol_id, available_meta)
            return serializer.serialize(schema.text, obj, header, topic, is_key=is_key)

    def _get_store(self, serializer: AbstractSerializer) -> AbstractDescriptionStore:
        serializers_store = getattr(serializer, 'store', None)
        if serializers_store is not None:
            return serializers_store
        assert self._store is not None
        return self._store

    def _get_serializer(self, is_key: bool) -> AbstractSerializer:
        return self._key_serializer if is_key else self._value_serializer
