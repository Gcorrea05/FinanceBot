from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
)

from app.bot.bot import FinanceBot


VALID_TEST_TOKEN = (
    "123456789:"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ_"
    "abcdefghi123456789"
)


def test_finance_bot_registers_handlers():
    bot = FinanceBot(
        token=VALID_TEST_TOKEN
    )

    handlers = bot.application.handlers[0]

    conversation_handlers = [
        handler
        for handler in handlers
        if isinstance(
            handler,
            ConversationHandler,
        )
    ]

    assert len(conversation_handlers) >= 2

    assert any(
        isinstance(
            handler,
            CommandHandler,
        )
        for handler in handlers
    )

    assert any(
        isinstance(
            handler,
            MessageHandler,
        )
        for handler in handlers
    )
