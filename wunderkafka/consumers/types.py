from __future__ import annotations

import time
from typing import Generic, Optional, TypeVar, Any, Dict

from pydantic import BaseModel, ConfigDict, Field, model_validator

M = TypeVar("M")


class PayloadError(BaseModel):
    description: str


class StreamResult(BaseModel, Generic[M]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    payload: Optional[Dict[str, Any]] = None
    error: Optional[PayloadError] = None
    msg: M
    t0: float = Field(default_factory=time.perf_counter)

    @property
    def ok(self) -> bool:
        return self.error is None and self.payload is not None

    @property
    def lifetime(self) -> float:
        return time.perf_counter() - self.t0

    @model_validator(mode="after")
    def verify_mutually_exclusive(self) -> StreamResult:
        if self.payload is None and self.error is None:
            raise ValueError("payload and error cannot both be None")
        if self.payload is not None and self.error is not None:
            raise ValueError("payload and error cannot both be not None")
        return self
