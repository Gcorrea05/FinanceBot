from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_telegram_handler_does_not_import_database_models():
    source = (ROOT / "app/bot/handlers/expense_conversation.py").read_text(encoding="utf-8")
    assert "app.database.models" not in source
    assert "container.expense_service" in source


def test_api_uses_services_instead_of_sql_text():
    for path in (ROOT / "app/api/routes").glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "session.execute(text(" not in source, path


def test_obsolete_agent_layer_is_absent():
    assert not (ROOT / "app/agents").exists()
    assert not (ROOT / "app/api/routes/agent.py").exists()
