from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_production_files_exist():
    for path in (
        "compose.yml",
        "Dockerfile",
        "frontend/Dockerfile.prod",
        "frontend/nginx.conf",
        "scripts/production_up.ps1",
        "scripts/production_down.ps1",
        "scripts/backup_production.ps1",
        "scripts/validate_database.py",
    ):
        assert (ROOT / path).exists(), path


def test_compose_uses_migration_gate_and_persistent_sqlite_volume():
    source = (ROOT / "compose.yml").read_text(encoding="utf-8")
    assert "service_completed_successfully" in source
    assert "financebot_data:/app/data" in source
    assert "scripts.production_bootstrap" in source
    assert "${PRODUCTION_WEB_BIND_ADDRESS}:${PRODUCTION_WEB_PORT}:80" in source


def test_example_environment_is_never_runtime_source():
    source = (ROOT / "compose.yml").read_text(encoding="utf-8")
    assert ".env.example" not in source
    assert "env_file:" in source
    assert "- .env" in source
