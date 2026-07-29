from collections import defaultdict
from collections.abc import Callable

from app.events.model import DomainEvent

EventHandler = Callable[[DomainEvent], None]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        self._handlers[event_name].append(handler)

    def subscribe_many(
        self,
        event_names: tuple[str, ...],
        handler: EventHandler,
    ) -> None:
        for event_name in event_names:
            self.subscribe(event_name, handler)

    def dispatch(self, event: DomainEvent) -> None:
        handlers = [
            *self._handlers.get(event.name, []),
            *self._handlers.get("*", []),
        ]
        for handler in handlers:
            handler(event)
