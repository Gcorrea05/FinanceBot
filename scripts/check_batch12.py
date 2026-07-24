from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

from app.api.app import create_app


REQUIRED_FILES = {
    "app/repositories/report_repository.py",
    "app/services/report_service.py",
    "app/api/schemas/report.py",
    "app/api/routes/reports.py",
    "tests/test_report_service.py",
    "tests/test_api_reports.py",
    "frontend/src/pages/ReportsPage.tsx",
    "frontend/src/pages/ReportsPage.test.tsx",
    "frontend/src/components/TrendChart.tsx",
    "frontend/src/components/BreakdownBars.tsx",
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

    report_path = (
        "/api/v1/reports/overview"
    )

    if report_path not in paths:
        print(
            "[ERRO] Rota de relatorios ausente."
        )
        return 1

    methods = (
        application.openapi()
        .get("paths", {})
        .get(
            report_path,
            {},
        )
    )

    if "get" not in methods:
        print(
            "[ERRO] Metodo GET de relatorios ausente."
        )
        return 1

    script = ScriptDirectory.from_config(
        Config("alembic.ini")
    )

    if script.get_heads() != [
        "20260724_0002"
    ]:
        print(
            "[ERRO] O Batch 12 nao deve criar migration: "
            f"{script.get_heads()}"
        )
        return 1

    app_content = Path(
        "frontend/src/App.tsx"
    ).read_text(
        encoding="utf-8"
    )

    if "ReportsPage" not in app_content:
        print(
            "[ERRO] Pagina de relatorios nao registrada."
        )
        return 1

    reports_content = Path(
        "frontend/src/pages/ReportsPage.tsx"
    ).read_text(
        encoding="utf-8"
    )

    required_terms = {
        "TrendChart",
        "BreakdownBars",
        "Parcelamentos ativos",
        "Estabelecimentos",
    }

    missing_terms = sorted(
        term
        for term in required_terms
        if term not in reports_content
    )

    if missing_terms:
        print(
            "[ERRO] Secoes ausentes na interface:"
        )

        for term in missing_terms:
            print(f"  - {term}")

        return 1

    print(
        "[OK] API de relatorios registrada."
    )
    print(
        "[OK] Comparacao mensal configurada."
    )
    print(
        "[OK] Gastos por categoria configurados."
    )
    print(
        "[OK] Ranking de estabelecimentos configurado."
    )
    print(
        "[OK] Visao de parcelamentos configurada."
    )
    print(
        "[OK] Nenhuma migration nova adicionada."
    )
    print(
        "[OK] Batch 12 validado."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
