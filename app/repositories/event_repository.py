from datetime import datetime, timedelta

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database.models.domain_event import DomainEventRecord
from app.events.model import DomainEvent


class EventRepository:
    def __init__(self, session: Session):
        self.session = session

    def enqueue(self, event: DomainEvent) -> DomainEventRecord:
        record = DomainEventRecord(
            event_id=event.event_id,
            event_name=event.name,
            aggregate_type=event.aggregate_type,
            aggregate_id=event.aggregate_id,
            payload=event.payload,
            status="pending",
            available_at=datetime.utcnow(),
            occurred_at=event.occurred_at,
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def list_pending(self, *, limit: int = 100) -> list[DomainEventRecord]:
        now = datetime.utcnow()
        statement = (
            select(DomainEventRecord)
            .where(
                DomainEventRecord.status.in_(("pending", "failed")),
                or_(
                    DomainEventRecord.available_at.is_(None),
                    DomainEventRecord.available_at <= now,
                ),
            )
            .order_by(DomainEventRecord.created_at, DomainEventRecord.id)
            .limit(limit)
        )
        return list(self.session.scalars(statement).all())

    def mark_processed(self, record: DomainEventRecord) -> None:
        record.status = "processed"
        record.processed_at = datetime.utcnow()
        record.last_error = None
        self.session.commit()

    def mark_failed(self, record: DomainEventRecord, error: Exception) -> None:
        record.attempts += 1
        record.status = "failed"
        record.last_error = str(error)[:2000]
        delay = min(60 * (2 ** min(record.attempts, 6)), 3600)
        record.available_at = datetime.utcnow() + timedelta(seconds=delay)
        self.session.commit()
