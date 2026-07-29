from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class DomainEventRecord(Base):
    __tablename__ = "domain_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str] = mapped_column(
        String(40), nullable=False, unique=True, index=True
    )
    event_name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    aggregate_type: Mapped[str] = mapped_column(
        String(60), nullable=False, index=True
    )
    aggregate_id: Mapped[str | None] = mapped_column(
        String(80), nullable=True, index=True
    )
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    available_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
