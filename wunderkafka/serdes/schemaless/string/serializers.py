from typing import Any, Optional

from confluent_kafka.serialization import StringSerializer as _StringSerializer

from wunderkafka.serdes.abc import AbstractSerializer, AbstractDescriptionStore
from wunderkafka.serdes.store import StringRepo


class StringSerializer(AbstractSerializer):
    def __init__(self, store: Optional[AbstractDescriptionStore] = None) -> None:
        self.store = store or StringRepo()
        self._serializer = _StringSerializer()

    def serialize(
        self,
        schema: str,
        payload: Any,
        header: Optional[bytes] = None,
        topic: Optional[str] = None,
        *,
        is_key: Optional[bool] = None,
    ) -> bytes:
        return self._serializer(payload, None)
