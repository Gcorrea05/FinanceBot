from pathlib import Path
import json


REQUIRED_FILES = {
    "frontend/package.json",
    "frontend/vite.config.ts",
    "frontend/src/App.tsx",
    "frontend/src/api/client.ts",
    "frontend/src/pages/DashboardPage.tsx",
    "frontend/src/pages/ExpensesPage.tsx",
    "frontend/src/pages/ReceivablesPage.tsx",
}


def main() -> int:
    missing = sorted(
        path
        for path in REQUIRED_FILES
        if not Path(path).exists()
    )

    if missing:
        print("[ERRO] Arquivos ausentes no frontend:")
        for path in missing:
            print(f"  - {path}")
        return 1

    package = json.loads(
        Path("frontend/package.json").read_text(
            encoding="utf-8"
        )
    )

    scripts = package.get("scripts", {})
    required_scripts = {
        "dev",
        "build",
        "test",
        "typecheck",
    }

    absent_scripts = sorted(
        required_scripts.difference(scripts)
    )

    if absent_scripts:
        print(
            "[ERRO] Scripts npm ausentes: "
            f"{absent_scripts}"
        )
        return 1

    app_content = Path(
        "frontend/src/App.tsx"
    ).read_text(encoding="utf-8")

    for page in (
        "DashboardPage",
        "ExpensesPage",
        "ReceivablesPage",
    ):
        if page not in app_content:
            print(
                f"[ERRO] Pagina nao registrada: {page}"
            )
            return 1

    print("[OK] Estrutura React + TypeScript encontrada.")
    print("[OK] Dashboard inicial registrado.")
    print("[OK] Consulta de despesas registrada.")
    print("[OK] Valores a receber registrados.")
    print("[OK] Batch 9 validado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
