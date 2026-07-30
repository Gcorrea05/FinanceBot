from __future__ import annotations

from alembic.runtime.migration import MigrationContext
from sqlalchemy import inspect, text

from app.database.session import engine

EXPECTED_TABLES = {
    "alembic_version",
    "budgets",
    "categories",
    "domain_events",
    "expense_installments",
    "expense_people",
    "expenses",
    "financial_profiles",
    "payment_methods",
    "people",
    "recurring_expense_occurrences",
    "recurring_expenses",
}


def validate() -> list[str]:
    errors: list[str] = []
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    missing = sorted(EXPECTED_TABLES - tables)
    if missing:
        errors.append(f"Tabelas ausentes: {missing}")

    with engine.connect() as connection:
        integrity = connection.exec_driver_sql("PRAGMA integrity_check").scalar()
        if integrity != "ok":
            errors.append(f"PRAGMA integrity_check: {integrity}")

        foreign_keys = connection.exec_driver_sql("PRAGMA foreign_key_check").all()
        if foreign_keys:
            errors.append(f"Foreign keys invalidas: {foreign_keys[:10]}")

        enabled = connection.exec_driver_sql("PRAGMA foreign_keys").scalar()
        if enabled != 1:
            errors.append("PRAGMA foreign_keys nao esta ativo.")

        journal = str(connection.exec_driver_sql("PRAGMA journal_mode").scalar()).lower()
        if journal != "wal":
            errors.append(f"journal_mode esperado WAL, encontrado {journal}.")

        busy = int(connection.exec_driver_sql("PRAGMA busy_timeout").scalar() or 0)
        if busy < 1000:
            errors.append(f"busy_timeout insuficiente: {busy} ms.")

        if "expenses" in tables:
            invalid_expenses = connection.execute(
                text("SELECT COUNT(*) FROM expenses WHERE purchase_value <= 0")
            ).scalar_one()
            if invalid_expenses:
                errors.append(f"Despesas com valor invalido: {invalid_expenses}")

        if "expense_installments" in tables:
            invalid_installments = connection.execute(
                text(
                    "SELECT COUNT(*) FROM expense_installments "
                    "WHERE installment_value <= 0 OR installment_number < 1 "
                    "OR total_installments < installment_number"
                )
            ).scalar_one()
            if invalid_installments:
                errors.append(f"Parcelas invalidas: {invalid_installments}")

        if "recurring_expense_occurrences" in tables:
            duplicates = connection.execute(
                text(
                    "SELECT COUNT(*) FROM ("
                    "SELECT recurring_expense_id, competence_year, competence_month "
                    "FROM recurring_expense_occurrences "
                    "GROUP BY recurring_expense_id, competence_year, competence_month "
                    "HAVING COUNT(*) > 1)"
                )
            ).scalar_one()
            if duplicates:
                errors.append(f"Ocorrencias recorrentes duplicadas: {duplicates}")

        context = MigrationContext.configure(connection)
        current = context.get_current_revision()
        if current != "20260729_0006":
            errors.append(f"Migration atual incorreta: {current!r}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        return 1
    print("[OK] SQLite integrity_check: ok")
    print("[OK] Foreign keys: validas")
    print("[OK] WAL e busy_timeout: ativos")
    print("[OK] Valores e ocorrencias: consistentes")
    print("[OK] Migration: 20260729_0006")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
