from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class RegisteredSchema:
    schema_id: int
    schema: dict
    subject: str
    version: int

    references: Optional[dict] = None

    @property
    def uniq_key(self) -> Tuple[str, int]:
        return self.subject, self.schema_id
