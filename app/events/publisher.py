import logging

from app.events.bus import EventBus
from app.events.model import DomainEvent
from app.repositories.event_repository import EventRepository

logger = logging.getLogger(__name__)


class EventPublisher:
    def __init__(self, *, repository: EventRepository, bus: EventBus):
        self.repository = repository
        self.bus = bus

    def publish(self, event: DomainEvent) -> None:
        record = self.repository.enqueue(event)
        try:
            self.bus.dispatch(event)
        except Exception as error:
            self.repository.mark_failed(record, error)
            logger.exception("Falha ao processar evento %s.", event.name)
            return
        self.repository.mark_processed(record)
