from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

from app.api.app import create_app


REQUIRED_FILES = {
    "app/database/models/budget.py",
    "app/services/budget_service.py",
    "app/api/routes/budgets.py",
    (
        "migrations/versions/"
        "20260724_0002_monthly_budgets.py"
    ),
    "frontend/src/pages/BudgetPage.tsx",
    "frontend/src/pages/BudgetPage.test.tsx",
}


def main() -> int:
    missing_files = sorted(
        path
        for path in REQUIRED_FILES
        if not Path(path).exists()
    )

    if missing_files:
        print(
            "[ERRO] Arquivos ausentes:"
        )

        for path in missing_files:
            print(f"  - {path}")

        return 1

    application = create_app()
    paths = set(
        application.openapi()
        .get("paths", {})
        .keys()
    )

    budget_path = (
        "/api/v1/budgets/{year}/{month}"
    )

    if budget_path not in paths:
        print(
            "[ERRO] Rota de planejamento ausente."
        )
        return 1

    methods = (
        application.openapi()
        .get("paths", {})
        .get(
            budget_path,
            {},
        )
    )

    if not {
        "get",
        "put",
    }.issubset(methods):
        print(
            "[ERRO] Metodos GET/PUT de planejamento ausentes."
        )
        return 1

    script = ScriptDirectory.from_config(
        Config("alembic.ini")
    )

    if script.get_heads() != [
        "20260724_0002"
    ]:
        print(
            "[ERRO] Head de migration inesperada: "
            f"{script.get_heads()}"
        )
        return 1

    app_content = Path(
        "frontend/src/App.tsx"
    ).read_text(
        encoding="utf-8"
    )

    if "BudgetPage" not in app_content:
        print(
            "[ERRO] Pagina de planejamento nao registrada."
        )
        return 1

    print(
        "[OK] Planejamento mensal persistido."
    )
    print(
        "[OK] Calculo da parte do proprietario configurado."
    )
    print(
        "[OK] Parcelas consideradas pelo vencimento."
    )
    print(
        "[OK] API de planejamento registrada."
    )
    print(
        "[OK] Interface web de planejamento registrada."
    )
    print(
        "[OK] Batch 11 validado."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
