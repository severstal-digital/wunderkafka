"""
This module contains the high-level pipeline to produce messages with a nested producer.

It is intended to be testable enough due to composition of dependencies.

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
        schema_registry: AbstractSchemaRegistry,
        header_packer: HeaderPacker,
        serializer: AbstractSerializer,
        store: AbstractDescriptionStore,
        # ToDo: switch mapping to something like consumer's TopicSubscription?
        mapping: Optional[Dict[TopicName, MessageDescription]] = None,
        *,
        lazy: bool = False,
    ) -> None:
        """
        Init producer with specific dependencies and prepare it to work against specified topic(s).

        :param producer:            Producer implementation to send messages.
        :param schema_registry:     Schema registry client.
        :param header_packer:       Callable to form binary headers.
        :param serializer:          Message serializer.
        :param store:               Specific store to provide schema text extraction from schema description.
        :param mapping:             Per-topic definition of value and/or key schema descriptions.
        :param lazy:                If True, defer schema registry publication, otherwise schema will be registered
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

        for topic, description in self._mapping.items():
            if isinstance(description, (tuple, list)):
                msg_value, msg_key = description
                self.set_target_topic(topic, msg_value, msg_key, lazy=lazy)
            else:
                self.set_target_topic(topic, description, lazy=lazy)

    def flush(self, timeout: Optional[float] = None) -> int:   # noqa: D102  # docstring inherited from superclass.
        if timeout is None:
            return self._producer.flush()
        return self._producer.flush(timeout)

    def set_target_topic(  # noqa: D102  # docstring inherited from superclass.
        self,
        topic: str,
        value: Any,  # noqa: WPS110  # Domain. inherited from superclass.
        key: Any = None,
        *,
        lazy: bool = False,
    ) -> None:
        self._store.add(topic, value, key)
        if not lazy:
            value_descr = self._store.get(topic)
            self._check_schema(topic, value_descr)
            if key is not None:
                key_descr = self._store.get(topic, is_key=True)
                self._check_schema(topic, key_descr, is_key=True)

    def send_message(  # noqa: D102,WPS211  # inherited from superclass.
        self,
        topic: str,
        value: MsgValue = None,  # noqa: WPS110  # Domain. inherited from superclass.
        key: MsgKey = None,
        partition: Optional[int] = None,
        on_delivery: Optional[DeliveryCallback] = error_callback,
        *args: Any,
        blocking: bool = False,
        protocol_id: int = 1,
        **kwargs: Any,
    ) -> None:
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
    ) -> SRMeta:
        """
        Ensure that we have schema's ids necessary to create message's header.

        :param topic:   Target topic against which we are working for this call.
        :param schema:  Schema container to be registered. Should contain text.
        :param is_key:  If True, schema will be requested as message key, message value otherwise.
        :param force:   If True, do not reuse cached results, always request Schema Registry.

        :raises ValueError: If received no schema from DescriptionStore.

        :return:        Container with schema's ids.
        """
        if schema is None:
            raise ValueError("Couldn't check schema from store.")
        uid = (topic, schema.text, is_key)

        if force is False:
            meta = self._checked.get(uid)
            if meta is not None:
                return meta
        meta = self._sr.register_schema(topic, schema.text, is_key=is_key)
        self._checked[uid] = meta
        return meta

    # ToDo (tribunsky.kir): Maybe, this method should be public for more simple extension.
    #                       'Template' pattern never works anyway.
    def _encode(self, topic: str, obj: Any, protocol_id: int, is_key: bool = False) -> Optional[bytes]:  # noqa: WPS110
        if obj is None:
            return None

        schema = self._store.get(topic, is_key=is_key)
        if schema is not None:
            # ToDo (tribunsky.kir): make it symmetrical with HeaderParser
            available_meta = self._check_schema(topic, schema, is_key=is_key)
            # ToDo (tribunsky.kir): add to (de)serialization ability to include the whole schema to the header.
            header = self._header_packer(protocol_id, available_meta)
            return self._serializer.serialize(schema.text, obj, header)
        # ToDo (tribunsky.kir): In the sake of mypy, re-do (add strict flag or something like that).
        logger.warning('Missing schema for {0} (key: {1}'.format(topic, is_key))
        return None
