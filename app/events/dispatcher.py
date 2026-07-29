import logging

from app.events.bus import EventBus
from app.events.model import DomainEvent
from app.repositories.event_repository import EventRepository

logger = logging.getLogger(__name__)


class EventDispatcher:
    def __init__(self, *, repository: EventRepository, bus: EventBus):
        self.repository = repository
        self.bus = bus

    def process_pending(self, *, limit: int = 100) -> tuple[int, int]:
        processed = failed = 0
        for record in self.repository.list_pending(limit=limit):
            event = DomainEvent(
                event_id=record.event_id,
                name=record.event_name,
                aggregate_type=record.aggregate_type,
                aggregate_id=record.aggregate_id,
                payload=dict(record.payload or {}),
                occurred_at=record.occurred_at,
            )
            try:
                self.bus.dispatch(event)
            except Exception as error:
                failed += 1
                self.repository.mark_failed(record, error)
                logger.exception("Falha no retry do evento %s.", event.name)
            else:
                processed += 1
                self.repository.mark_processed(record)
        return processed, failed
