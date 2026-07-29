from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class DomainEvent:
    event_id: str
    name: str
    aggregate_type: str
    aggregate_id: str | None
    payload: dict[str, Any]
    occurred_at: datetime

    @classmethod
    def new(
        cls,
        *,
        name: str,
        aggregate_type: str,
        aggregate_id: int | str | None,
        payload: dict[str, Any] | None = None,
    ) -> "DomainEvent":
        return cls(
            event_id=uuid4().hex,
            name=name,
            aggregate_type=aggregate_type,
            aggregate_id=None if aggregate_id is None else str(aggregate_id),
            payload=payload or {},
            occurred_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
