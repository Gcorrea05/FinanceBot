import asyncio
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.bot.handlers.reference_data import (
    list_categories,
    list_payment_methods,
)
from app.bot.handlers.start import (
    menu_handler,
    start,
)


def make_update(text: str = ""):
    message = SimpleNamespace(
        text=text,
        reply_text=AsyncMock(),
    )

    return SimpleNamespace(
        effective_message=message,
    )


def test_start_sends_main_menu():
    update = make_update()

    asyncio.run(
        start(
            update,
            SimpleNamespace(),
        )
    )

    reply_mock = (
        update.effective_message.reply_text
    )

    reply_mock.assert_awaited_once()

    call = reply_mock.await_args

    assert call is not None
    assert "reply_markup" in call.kwargs


def test_unknown_menu_text_returns_guidance():
    update = make_update(
        "texto desconhecido"
    )

    asyncio.run(
        menu_handler(
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
    assert "Nao reconheci" in call.kwargs["text"]


def test_list_categories_uses_lookup_service():
    update = make_update()

    lookup_service = SimpleNamespace(
        list_category_names=lambda: [
            "Alimentacao",
            "Mercado",
        ]
    )

    fake_container = SimpleNamespace(
        lookup_service=lookup_service
    )

    @contextmanager
    def fake_container_context():
        yield fake_container

    with patch(
        (
            "app.bot.handlers.reference_data."
            "container_context"
        ),
        fake_container_context,
    ):
        asyncio.run(
            list_categories(
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

    response = call.kwargs["text"]

    assert "Alimentacao" in response
    assert "Mercado" in response


def test_list_payment_methods_uses_lookup_service():
    update = make_update()

    lookup_service = SimpleNamespace(
        list_payment_method_names=lambda: [
            "Pix",
            "Credito",
        ]
    )

    fake_container = SimpleNamespace(
        lookup_service=lookup_service
    )

    @contextmanager
    def fake_container_context():
        yield fake_container

    with patch(
        (
            "app.bot.handlers.reference_data."
            "container_context"
        ),
        fake_container_context,
    ):
        asyncio.run(
            list_payment_methods(
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

    response = call.kwargs["text"]

    assert "Pix" in response
    assert "Credito" in response
