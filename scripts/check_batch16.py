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
    "scripts/list_production_backups.ps1",
    "scripts/backup_sqlite.py",
    "scripts/restore_sqlite.py",
    ".github/workflows/ci.yml",
    "docs/DEPLOYMENT.md",
    "SECURITY.md",
    "tests/test_production_assets.py",
)


def main() -> int:
    missing = [
        path
        for path in REQUIRED
        if not Path(path).exists()
    ]

    for path in missing:
        print(
            f"[ERROR] Arquivo ausente: {path}"
        )

    if missing:
        return 1

    compose = Path(
        "docker-compose.prod.yml"
    ).read_text(encoding="utf-8")

    checks = {
        "Ambiente real em .env":
            "env_file:\n    - .env"
            in compose,
        "Sem leitura de .env.example":
            ".env.example"
            not in compose,
        "SQLite persistente":
            "financebot_data:/app/data"
            in compose,
        "API sem porta publica":
            "proxy_pass http://api:8000"
            in Path(
                "frontend/nginx.conf"
            ).read_text(
                encoding="utf-8"
            ),
        "Scheduler arquitetural":
            "app.automation.worker"
            in compose,
        "Migration 0005 preservada":
            Path(
                "migrations/versions/"
                "20260724_0005_"
                "architecture_hardening.py"
            ).exists(),
        "Nenhuma migration 0006":
            not any(
                Path(
                    "migrations/versions"
                ).glob(
                    "*0006*.py"
                )
            ),
        "Backup e restauracao":
            Path(
                "scripts/backup_sqlite.py"
            ).exists()
            and Path(
                "scripts/restore_sqlite.py"
            ).exists(),
        "CI configurado":
            Path(
                ".github/workflows/ci.yml"
            ).exists(),
    }

    failed = False

    for label, ok in checks.items():
        print(
            f"[{'OK' if ok else 'ERROR'}] "
            f"{label}."
        )
        failed = failed or not ok

    if failed:
        return 1

    print(
        "[OK] Batch 16 final validado."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
