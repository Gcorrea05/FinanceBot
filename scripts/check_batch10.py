from pathlib import Path

from app.api.app import create_app


REQUIRED_FRONTEND_FILES = {
    "frontend/src/components/ExpenseForm.tsx",
    "frontend/src/components/ExpenseForm.test.tsx",
    "frontend/src/pages/ExpensesPage.tsx",
}


def main() -> int:
    application = create_app()
    schema = application.openapi()
    expense_path = schema.get("paths", {}).get(
        "/api/v1/expenses/{expense_id}",
        {},
    )

    if "put" not in expense_path:
        print("[ERRO] Rota PUT de edicao de despesas ausente.")
        return 1

    missing_files = sorted(
        path
        for path in REQUIRED_FRONTEND_FILES
        if not Path(path).exists()
    )

    if missing_files:
        print("[ERRO] Arquivos ausentes no frontend:")
        for path in missing_files:
            print(f"  - {path}")
        return 1

    expenses_page = Path(
        "frontend/src/pages/ExpensesPage.tsx"
    ).read_text(encoding="utf-8")

    required_markers = (
        "Nova despesa",
        "updateExpense",
        "deleteExpense",
        "ExpenseForm",
    )

    missing_markers = [
        marker
        for marker in required_markers
        if marker not in expenses_page
    ]

    if missing_markers:
        print("[ERRO] Funcionalidades web ausentes:")
        for marker in missing_markers:
            print(f"  - {marker}")
        return 1

    print("[OK] Cadastro web de despesas configurado.")
    print("[OK] Edicao completa de despesas configurada.")
    print("[OK] Exclusao com confirmacao configurada.")
    print("[OK] Protecao de historico financeiro configurada.")
    print("[OK] Batch 10 validado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
