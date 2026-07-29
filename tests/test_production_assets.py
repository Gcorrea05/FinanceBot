from pathlib import Path


REQUIRED = (
    "Dockerfile",
    ".dockerignore",
    "docker-compose.prod.yml",
    "frontend/Dockerfile.prod",
    "frontend/nginx.conf",
    "scripts/prepare_production_env.ps1",
    "scripts/production_up.ps1",
    "scripts/production_down.ps1",
    "scripts/production_status.ps1",
    "scripts/production_logs.ps1",
    "scripts/backup_production.ps1",
    "scripts/restore_production.ps1",
    "scripts/backup_sqlite.py",
    "scripts/restore_sqlite.py",
    ".github/workflows/ci.yml",
    "docs/DEPLOYMENT.md",
    "SECURITY.md",
)


def test_production_assets_exist():
    missing = [
        path
        for path in REQUIRED
        if not Path(path).exists()
    ]

    assert not missing


def test_production_reads_real_env():
    compose = Path(
        "docker-compose.prod.yml"
    ).read_text(encoding="utf-8")

    prepare = Path(
        "scripts/prepare_production_env.ps1"
    ).read_text(encoding="utf-8")

    assert "env_file:" in compose
    assert "- .env" in compose
    assert "--env-file .env" in prepare or (
        "Arquivo .env nao encontrado"
        in prepare
    )
    assert ".env.example" not in compose


def test_only_web_has_public_port():
    compose = Path(
        "docker-compose.prod.yml"
    ).read_text(encoding="utf-8")

    before_web = compose.split(
        "  web:",
        1,
    )[0]

    assert "ports:" not in before_web
    assert (
        "${PRODUCTION_WEB_BIND_ADDRESS}:"
        "${PRODUCTION_WEB_PORT}:80"
        in compose
    )


def test_scheduler_uses_new_architecture():
    compose = Path(
        "docker-compose.prod.yml"
    ).read_text(encoding="utf-8")

    assert "  scheduler:" in compose
    assert "app.automation.worker" in compose
    assert "service_completed_successfully" in compose


def test_sqlite_is_persistent():
    compose = Path(
        "docker-compose.prod.yml"
    ).read_text(encoding="utf-8")

    assert "financebot_data:/app/data" in compose
    assert (
        "PRODUCTION_DATABASE_URL"
        in compose
    )
