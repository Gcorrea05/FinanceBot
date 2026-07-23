import pytest

from app.config import (
    ConfigurationError,
    Settings,
)


def test_require_telegram_token_rejects_empty_value():
    settings = Settings(
        DATABASE_URL="sqlite:///test.db",
        TELEGRAM_TOKEN="   ",
    )

    with pytest.raises(ConfigurationError):
        settings.require_telegram_token()


def test_require_telegram_token_returns_trimmed_value():
    settings = Settings(
        DATABASE_URL="sqlite:///test.db",
        TELEGRAM_TOKEN="  123456:TEST_TOKEN  ",
    )

    assert (
        settings.require_telegram_token()
        == "123456:TEST_TOKEN"
    )
