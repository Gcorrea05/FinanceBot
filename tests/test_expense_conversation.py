import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from telegram.ext import ConversationHandler

from app.bot.handlers.expense_conversation import (
    CONFIRM,
    DRAFT_KEY,
    NATURAL_TEXT,
    PAYMENT_KEY,
    PAYMENT_METHOD,
    cancel_expense,
    receive_natural_text,
    receive_payment_method,
    start_expense,
)
from app.bot.keyboards.expense import (
    PAYMENT_CREDIT_CARD,
    PAYMENT_PIX,
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


def test_start_expense_initializes_natural_flow():
    update = make_update()
    context = make_context()
    context.user_data[DRAFT_KEY] = object()
    context.user_data[PAYMENT_KEY] = "Pix"

    state = asyncio.run(
        start_expense(update, context)
    )

    assert state == NATURAL_TEXT
    assert DRAFT_KEY not in context.user_data
    assert PAYMENT_KEY not in context.user_data
    update.effective_message.reply_text.assert_awaited_once()


def test_natural_message_creates_draft_and_asks_payment():
    update = make_update(
        "tablet 1700 parcelado em 10x"
    )
    context = make_context()

    state = asyncio.run(
        receive_natural_text(update, context)
    )

    assert state == PAYMENT_METHOD

    draft = context.user_data[DRAFT_KEY]
    assert draft.description == "tablet"
    assert draft.installments == 10
    assert draft.is_installment is True


def test_installment_rejects_non_credit_payment():
    context = make_context()
    asyncio.run(
        receive_natural_text(
            make_update("tablet 1700 em 10x"),
            context,
        )
    )

    state = asyncio.run(
        receive_payment_method(
            make_update(PAYMENT_PIX),
            context,
        )
    )

    assert state == PAYMENT_METHOD
    assert PAYMENT_KEY not in context.user_data


def test_installment_accepts_credit_payment():
    context = make_context()
    asyncio.run(
        receive_natural_text(
            make_update("tablet 1700 em 10x"),
            context,
        )
    )

    state = asyncio.run(
        receive_payment_method(
            make_update(PAYMENT_CREDIT_CARD),
            context,
        )
    )

    assert state == CONFIRM
    assert (
        context.user_data[PAYMENT_KEY]
        == PAYMENT_CREDIT_CARD
    )


def test_cancel_clears_only_current_expense_draft():
    update = make_update("Cancelar")
    context = make_context()
    context.user_data.update(
        {
            DRAFT_KEY: object(),
            PAYMENT_KEY: "Pix",
            "other_data": "keep",
        }
    )

    state = asyncio.run(
        cancel_expense(update, context)
    )

    assert state == ConversationHandler.END
    assert DRAFT_KEY not in context.user_data
    assert PAYMENT_KEY not in context.user_data
    assert context.user_data["other_data"] == "keep"