from pathlib import Path


REQUIRED = (
    "app/imports/parser.py",
    "app/services/import_service.py",
    "app/repositories/import_repository.py",
    "app/database/models/import_batch.py",
    "app/api/routes/imports.py",
    "migrations/versions/20260724_0003_import_history.py",
    "frontend/src/pages/ImportsPage.tsx",
    "frontend/src/pages/imports.css",
)


def main() -> int:
    missing = [path for path in REQUIRED if not Path(path).exists()]
    if missing:
        for path in missing:
            print(f"[ERROR] Arquivo ausente: {path}")
        return 1

    route_text = Path("app/api/routes/__init__.py").read_text(encoding="utf-8")
    imports_route = Path("app/api/routes/imports.py").read_text(encoding="utf-8")
    parser_text = Path("app/imports/parser.py").read_text(encoding="utf-8")
    page_text = Path("frontend/src/pages/ImportsPage.tsx").read_text(encoding="utf-8")
    shell_text = Path("frontend/src/components/AppShell.tsx").read_text(encoding="utf-8")
    requirements = Path("requirements.txt").read_text(encoding="utf-8")

    checks = {
        "Rota de importacoes registrada": "imports_router" in route_text,
        "Inspecao de estrutura registrada": '"/inspect"' in imports_route,
        "Mapeamento por indice configurado": "ImportColumnMapping" in parser_text,
        "Sem validacao de nomes obrigatorios": "_validate_headers" not in parser_text,
        "Interface de mapeamento registrada": "Coluna da data" in page_text,
        "Menu de importacoes registrado": 'id: "imports"' in shell_text,
        "OpenPyXL configurado": "openpyxl" in requirements,
        "Multipart configurado": "python-multipart" in requirements,
    }
    failed = False
    for label, ok in checks.items():
        print(f"[{'OK' if ok else 'ERROR'}] {label}.")
        failed = failed or not ok
    if failed:
        return 1
    print("[OK] Batch 13 flexivel validado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
