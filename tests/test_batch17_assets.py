from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_compose_keeps_sqlite_and_single_public_entrypoint():
    compose = (ROOT / "compose.yml").read_text(encoding="utf-8")
    assert "sqlite:////app/data/finance.db" not in compose  # comes from .env, not hard-coded secret/config
    assert "financebot_data:/app/data" in compose
    assert "postgres" not in compose.lower()
    assert '"${PRODUCTION_WEB_BIND_ADDRESS}:${PRODUCTION_WEB_PORT}:80"' in compose


def test_old_compose_and_agents_were_removed():
    assert not (ROOT / "docker-compose.prod.yml").exists()
    assert not (ROOT / "app/agents").exists()


def test_payment_keyboard_has_only_supported_methods():
    source = (ROOT / "app/bot/keyboards/expense.py").read_text(encoding="utf-8")
    for value in ("Cartão de crédito", "Débito", "Pix", "Dinheiro"):
        assert value in source
