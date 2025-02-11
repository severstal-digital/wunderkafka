import json
from typing import Any, Optional

from wunderkafka.serdes.abc import AbstractSerializer
from wunderkafka.serdes.store import StringRepo


class SchemaLessJSONSerializer(AbstractSerializer):
    def __init__(self) -> None:
        self.store = StringRepo()

    def serialize(
        self,
        schema: str,
        obj: Any,
        header: Optional[bytes] = None,
        topic: Optional[str] = None,
        *,
        is_key: Optional[bool] = None,
    ) -> bytes:
        return json.dumps(obj, default=str).encode()
