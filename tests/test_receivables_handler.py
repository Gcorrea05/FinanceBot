import asyncio
from contextlib import contextmanager
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.bot.handlers.receivables import (
    RECEIVABLE_PERSON,
    start_receivables,
)


def test_start_receivables_shows_total():
    update = SimpleNamespace(
        effective_message=SimpleNamespace(
            text="/receber",
            reply_text=AsyncMock(),
        )
    )

    context = SimpleNamespace(
        user_data={},
        args=[],
    )

    summary = [
        SimpleNamespace(
            person_id=1,
            person_name="Tomas",
            total=Decimal("70.00"),
            pending_count=1,
        ),
        SimpleNamespace(
            person_id=2,
            person_name="Sofia",
            total=Decimal("50.00"),
            pending_count=2,
        ),
    ]

    service = SimpleNamespace(
        list_open_summary=lambda: summary
    )

    fake_container = SimpleNamespace(
        receivable_service=service
    )

    @contextmanager
    def fake_container_context():
        yield fake_container

    with patch(
        (
            "app.bot.handlers.receivables."
            "container_context"
        ),
        fake_container_context,
    ):
        state = asyncio.run(
            start_receivables(
                update,
                context,
            )
        )

    assert state == RECEIVABLE_PERSON

    call = (
        update.effective_message
        .reply_text
        .await_args
    )

    assert call is not None
    text = call.args[0]

    assert "Tomas" in text
    assert "Sofia" in text
    assert "R$ 120,00" in text
