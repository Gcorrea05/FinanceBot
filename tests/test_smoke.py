def test_core_modules_can_be_imported():
    from app.bot.bot import FinanceBot
    from app.config import Settings, settings
    from app.container import Container
    from app.database.session import create_database, get_session

    assert FinanceBot is not None
    assert Settings is not None
    assert settings.DATABASE_URL
    assert Container is not None
    assert callable(create_database)
    assert callable(get_session)
