from app.core.settings import Settings


def test_settings_keep_legacy_aliases():
    settings = Settings(
        DATABASE_URL="sqlite:///data/test.db",
        TELEGRAM_TOKEN="token",
    )

    assert settings.DATABASE_URL == "sqlite:///data/test.db"
    assert settings.TELEGRAM_TOKEN == "token"
    assert settings.telegram.token == "token"
