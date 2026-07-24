from pathlib import Path


REQUIRED = (
    "app/database/models/automation.py",
    "app/repositories/automation_repository.py",
    "app/services/automation_service.py",
    "app/notifications/telegram_notifier.py",
    "app/automation/worker.py",
    "app/api/routes/automations.py",
    "app/api/schemas/automation.py",
    "migrations/versions/20260724_0004_automations.py",
    "frontend/src/pages/AutomationsPage.tsx",
    "frontend/src/pages/automations.css",
    "scripts/run_automations.ps1",
)


def main() -> int:
    missing = [
        path
        for path in REQUIRED
        if not Path(path).exists()
    ]

    if missing:
        for path in missing:
            print(
                f"[ERROR] Arquivo ausente: {path}"
            )
        return 1

    routes = Path(
        "app/api/routes/__init__.py"
    ).read_text(encoding="utf-8")
    shell = Path(
        (
            "frontend/src/components/"
            "AppShell.tsx"
        )
    ).read_text(encoding="utf-8")
    bot = Path(
        "app/bot/bot.py"
    ).read_text(encoding="utf-8")
    migration_test = Path(
        "tests/test_migration_baseline.py"
    ).read_text(encoding="utf-8")

    checks = {
        (
            "Rota de automacoes registrada"
        ): "automations_router" in routes,
        (
            "Menu de automacoes registrado"
        ): 'id: "automations"' in shell,
        (
            "Comando de vinculacao registrado"
        ): '"notificacoes"' in bot,
        (
            "Worker independente registrado"
        ): (
            "python -m app.automation.worker"
            in Path(
                "scripts/run_automations.ps1"
            ).read_text(encoding="utf-8")
        ),
        (
            "Head de migration atualizado"
        ): "20260724_0004" in migration_test,
    }

    failed = False

    for label, ok in checks.items():
        print(
            f"[{'OK' if ok else 'ERROR'}] "
            f"{label}."
        )
        failed = (
            failed
            or not ok
        )

    if failed:
        return 1

    print(
        "[OK] Batch 14 validado."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
