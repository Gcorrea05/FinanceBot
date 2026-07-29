from app.events import DomainEvent, EventBus


def test_event_bus_dispatches_named_and_global_handlers():
    bus = EventBus()
    calls: list[str] = []

    bus.subscribe(
        "expense.created",
        lambda event: calls.append(f"named:{event.name}"),
    )
    bus.subscribe(
        "*",
        lambda event: calls.append(f"all:{event.name}"),
    )
    bus.dispatch(
        DomainEvent.new(
            name="expense.created",
            aggregate_type="expense",
            aggregate_id=10,
        )
    )

    assert calls == [
        "named:expense.created",
        "all:expense.created",
    ]
