import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.bot.handlers.start import (
    HELP_TEXT,
    help_command,
)


def test_help_exposes_only_quick_operations():
    normalized = HELP_TEXT.casefold()

    assert "/gasto" in normalized
    assert "/ultimos" in normalized
    assert "/receber" in normalized

    assert "/categorias" not in normalized
    assert "/pagamentos" not in normalized


def test_help_returns_main_menu():
    message = SimpleNamespace(
        reply_text=AsyncMock(),
    )

    update = SimpleNamespace(
        effective_message=message,
    )

    asyncio.run(
        help_command(
            update,
            SimpleNamespace(),
        )
    )

    call = message.reply_text.await_args

    assert call is not None
    assert "reply_markup" in call.kwargs
