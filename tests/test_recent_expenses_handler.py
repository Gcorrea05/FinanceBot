import asyncio
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.bot.handlers.recent_expenses import (
    show_recent_expenses,
)
from app.services.expense_query_service import (
    RecentExpense,
)


def make_update():
    message = SimpleNamespace(
        reply_text=AsyncMock(),
    )

    return SimpleNamespace(
        effective_message=message,
    )


def test_recent_expenses_handler_limits_and_formats():
    update = make_update()
    received = {}

    class QueryServiceStub:
        def list_recent(
            self,
            limit,
        ):
            received["limit"] = limit

            return [
                RecentExpense(
                    expense_id=1,
                    purchase_date=datetime(
                        2026,
                        7,
                        23,
                        10,
                        0,
                    ),
                    purchase_place=(
                        "Mercado Central"
                    ),
                    purchase_value=(
                        Decimal("150.75")
                    ),
                    category_name="Mercado",
                    payment_method_name="Pix",
                    is_installment=False,
                    is_shared=True,
                )
            ]

    fake_container = SimpleNamespace(
        expense_query_service=(
            QueryServiceStub()
        )
    )

    @contextmanager
    def fake_container_context():
        yield fake_container

    with patch(
        (
            "app.bot.handlers.recent_expenses."
            "container_context"
        ),
        fake_container_context,
    ):
        asyncio.run(
            show_recent_expenses(
                update,
                SimpleNamespace(),
            )
        )

    assert received["limit"] == 5

    call = (
        update.effective_message
        .reply_text
        .await_args
    )

    assert call is not None

    text = call.args[0]

    assert "Mercado Central" in text
    assert "150,75" in text
    assert "compartilhada" in text
    assert "reply_markup" in call.kwargs


def test_recent_expenses_handler_handles_empty_list():
    update = make_update()

    query_service = SimpleNamespace(
        list_recent=lambda limit: []
    )

    fake_container = SimpleNamespace(
        expense_query_service=query_service
    )

    @contextmanager
    def fake_container_context():
        yield fake_container

    with patch(
        (
            "app.bot.handlers.recent_expenses."
            "container_context"
        ),
        fake_container_context,
    ):
        asyncio.run(
            show_recent_expenses(
                update,
                SimpleNamespace(),
            )
        )

    call = (
        update.effective_message
        .reply_text
        .await_args
    )

    assert call is not None
    assert "Nenhum lancamento" in call.args[0]
    assert "reply_markup" in call.kwargs
