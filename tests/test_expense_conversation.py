import asyncio
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from telegram.ext import ConversationHandler

from app.bot.handlers.expense_conversation import (
    CONFIRM,
    CURRENT_STATE_KEY,
    DRAFT_KEY,
    HISTORY_KEY,
    INSTALLMENT_CHOICE,
    NOTES,
    PURCHASE_DATE,
    PURCHASE_PLACE,
    SHARED_CHOICE,
    cancel_expense,
    confirm_expense,
    go_back,
    receive_installment_choice,
    receive_shared_choice,
    start_expense,
)
from app.schemas.expense.shared_person import (
    SharedPersonCreate,
)


def make_update(text: str = ""):
    message = SimpleNamespace(
        text=text,
        reply_text=AsyncMock(),
    )

    return SimpleNamespace(
        effective_message=message,
    )


def make_context():
    return SimpleNamespace(
        user_data={},
    )


def test_start_expense_initializes_flow():
    update = make_update()
    context = make_context()

    state = asyncio.run(
        start_expense(
            update,
            context,
        )
    )

    assert state == PURCHASE_DATE
    assert context.user_data[DRAFT_KEY] == {}
    assert (
        context.user_data[CURRENT_STATE_KEY]
        == PURCHASE_DATE
    )
    assert context.user_data[HISTORY_KEY] == []


def test_non_installment_skips_installment_details():
    update = make_update("Nao")
    context = make_context()

    context.user_data[DRAFT_KEY] = {}
    context.user_data[CURRENT_STATE_KEY] = (
        INSTALLMENT_CHOICE
    )
    context.user_data[HISTORY_KEY] = []

    state = asyncio.run(
        receive_installment_choice(
            update,
            context,
        )
    )

    assert state == SHARED_CHOICE

    draft = context.user_data[DRAFT_KEY]

    assert draft["is_installment"] is False
    assert draft["installments"] == 1
    assert (
        draft["first_installment_due_date"]
        is None
    )


def test_non_shared_skips_shared_details():
    update = make_update("Nao")
    context = make_context()

    context.user_data[DRAFT_KEY] = {}
    context.user_data[CURRENT_STATE_KEY] = (
        SHARED_CHOICE
    )
    context.user_data[HISTORY_KEY] = []

    state = asyncio.run(
        receive_shared_choice(
            update,
            context,
        )
    )

    assert state == NOTES

    draft = context.user_data[DRAFT_KEY]

    assert draft["is_shared"] is False
    assert draft["shared_people"] == ()


def test_go_back_returns_previous_state():
    update = make_update("Voltar")
    context = make_context()

    context.user_data[DRAFT_KEY] = {}
    context.user_data[CURRENT_STATE_KEY] = (
        PURCHASE_PLACE
    )
    context.user_data[HISTORY_KEY] = [
        PURCHASE_DATE
    ]

    state = asyncio.run(
        go_back(
            update,
            context,
        )
    )

    assert state == PURCHASE_DATE
    assert context.user_data[HISTORY_KEY] == []


def test_cancel_clears_only_expense_flow():
    update = make_update("Cancelar")
    context = make_context()

    context.user_data.update(
        {
            DRAFT_KEY: {"value": 1},
            CURRENT_STATE_KEY: PURCHASE_DATE,
            HISTORY_KEY: [],
            "other_data": "keep",
        }
    )

    state = asyncio.run(
        cancel_expense(
            update,
            context,
        )
    )

    assert state == ConversationHandler.END
    assert DRAFT_KEY not in context.user_data
    assert (
        context.user_data["other_data"]
        == "keep"
    )


def test_confirm_persists_expense():
    update = make_update("Confirmar")
    context = make_context()

    context.user_data[DRAFT_KEY] = {
        "purchase_date": datetime(
            2026,
            7,
            23,
        ),
        "purchase_place": "Mercado",
        "purchase_value": Decimal("100.00"),
        "category": "Mercado",
        "payment_method": "Pix",
        "is_installment": True,
        "installments": 2,
        "first_installment_due_date": date(
            2026,
            7,
            23,
        ),
        "is_shared": True,
        "shared_people": (
            SharedPersonCreate(
                name="Ana",
                amount=Decimal("20.00"),
            ),
        ),
        "notes": "Teste",
    }
    context.user_data[CURRENT_STATE_KEY] = CONFIRM
    context.user_data[HISTORY_KEY] = []

    saved = {}

    class ExpenseServiceStub:
        def create_expense(self, data):
            saved["data"] = data
            return SimpleNamespace(id=99)

    fake_container = SimpleNamespace(
        expense_service=ExpenseServiceStub()
    )

    @contextmanager
    def fake_container_context():
        yield fake_container

    with patch(
        (
            "app.bot.handlers.expense_conversation."
            "container_context"
        ),
        fake_container_context,
    ):
        state = asyncio.run(
            confirm_expense(
                update,
                context,
            )
        )

    assert state == ConversationHandler.END
    assert saved["data"].installments == 2
    assert saved["data"].is_shared is True
    assert saved["data"].shared_people[0].name == "Ana"
    assert DRAFT_KEY not in context.user_data
