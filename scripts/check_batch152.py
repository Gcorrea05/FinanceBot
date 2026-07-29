from pathlib import Path

REQUIRED = (
    "app/core/settings.py",
    "app/core/logging.py",
    "app/events/bus.py",
    "app/events/publisher.py",
    "app/events/dispatcher.py",
    "app/database/models/domain_event.py",
    "app/repositories/event_repository.py",
    "app/scheduler/registry.py",
    "app/scheduler/jobs.py",
    "app/agents/finance_agent.py",
    "app/services/dashboard_service.py",
    "app/api/routes/dashboard.py",
    "app/api/routes/agent.py",
    "migrations/versions/20260724_0005_architecture_hardening.py",
    "tests/test_architecture_boundaries.py",
    "docs/ARCHITECTURE.md",
)


def main() -> int:
    missing = [path for path in REQUIRED if not Path(path).exists()]
    for path in missing:
        print(f"[ERROR] Arquivo ausente: {path}")
    if missing:
        return 1

    migration = Path(
        "migrations/versions/20260724_0005_architecture_hardening.py"
    ).read_text(encoding="utf-8")

    checks = {
        "Configuracoes centralizadas": "class Settings" in Path(
            "app/core/settings.py"
        ).read_text(encoding="utf-8"),
        "Eventos persistentes": "domain_events" in migration,
        "Scheduler geral": "SchedulerRunner" in Path(
            "app/scheduler/registry.py"
        ).read_text(encoding="utf-8"),
        "Agent sem SQL": "app.repositories" not in Path(
            "app/agents/finance_agent.py"
        ).read_text(encoding="utf-8"),
        "Dashboard analitico": "/overview" in Path(
            "app/api/routes/dashboard.py"
        ).read_text(encoding="utf-8"),
        "Sem trigger financeiro": "CREATE TRIGGER" not in migration,
    }

    failed = False
    for label, ok in checks.items():
        print(f"[{'OK' if ok else 'ERROR'}] {label}.")
        failed = failed or not ok

    if failed:
        return 1

    print("[OK] Batch 15.2 validado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
