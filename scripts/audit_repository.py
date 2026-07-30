from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = (
    "compose.yml",
    "app/domain/natural_expense_parser.py",
    "app/database/models/recurring_expense.py",
    "app/services/future_planning_service.py",
    "scripts/validate_database.py",
    "migrations/versions/20260729_0006_recurring_future_and_sqlite_hardening.py",
    "frontend/src/pages/FuturePage.tsx",
)

FORBIDDEN = (
    "docker-compose.prod.yml",
    "app/agents",
    "app/api/routes/agent.py",
    "app/api/schemas/agent.py",
    "scripts/run_web.ps1",
    "scripts/run_automations.ps1",
)


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).exists():
            errors.append(f"Arquivo obrigatorio ausente: {relative}")
    for relative in FORBIDDEN:
        if (ROOT / relative).exists():
            errors.append(f"Artefato obsoleto presente: {relative}")

    root_installers = sorted(ROOT.glob("FinanceBot_Batch*.ps1"))
    if root_installers:
        errors.append("Instaladores historicos ainda presentes na raiz.")

    compose = (ROOT / "compose.yml").read_text(encoding="utf-8")
    for service in ("migrate:", "api:", "bot:", "scheduler:", "web:"):
        if service not in compose:
            errors.append(f"Servico ausente no Compose: {service}")
    if "postgres" in compose.casefold():
        errors.append("O Compose nao pode introduzir PostgreSQL.")
    if "financebot_data:/app/data" not in compose:
        errors.append("Volume persistente do SQLite ausente.")

    expense_model = (ROOT / "app/database/models/expense.py").read_text(encoding="utf-8")
    if "Mapped[Decimal]" not in expense_model or "Numeric(" not in expense_model:
        errors.append("Expense.purchase_value nao esta em Decimal/Numeric.")

    scheduler = (ROOT / "app/scheduler/jobs.py").read_text(encoding="utf-8")
    if "source.backup(backup)" not in scheduler:
        errors.append("Backup online do SQLite nao utiliza sqlite3.backup.")
    if "shutil.copy2" in scheduler:
        errors.append("Copia bruta do banco SQLite ainda presente.")

    keyboard = (ROOT / "app/bot/keyboards/expense.py").read_text(encoding="utf-8")
    for payment in ("Cartão de crédito", "Débito", "Pix", "Dinheiro"):
        if payment not in keyboard:
            errors.append(f"Pagamento ausente no Telegram: {payment}")

    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        return 1
    print("[OK] Auditoria estrutural do Batch 17 concluida.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
