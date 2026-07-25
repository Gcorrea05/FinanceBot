from pathlib import Path


REQUIRED = (
    'app/services/intelligence_service.py',
    'app/api/routes/intelligence.py',
    'app/api/schemas/intelligence.py',
    'frontend/src/pages/IntelligencePage.tsx',
    'frontend/src/pages/intelligence.css',
    'tests/test_intelligence_service.py',
    'tests/test_api_intelligence.py',
    'docs/INTELLIGENCE.md',
)


def main() -> int:
    missing = [path for path in REQUIRED if not Path(path).exists()]
    if missing:
        for path in missing:
            print(f'[ERROR] Arquivo ausente: {path}')
        return 1

    routes = Path('app/api/routes/__init__.py').read_text(encoding='utf-8')
    shell = Path('frontend/src/components/AppShell.tsx').read_text(encoding='utf-8')
    service = Path('app/services/intelligence_service.py').read_text(encoding='utf-8')
    migration_test = Path('tests/test_migration_baseline.py').read_text(encoding='utf-8')

    checks = {
        'Rota de inteligencia registrada': 'intelligence_router' in routes,
        'Menu de inteligencia registrado': 'id: "intelligence"' in shell,
        'Projecao explicavel registrada': 'def _forecast' in service,
        'Deteccao de anomalias registrada': 'def _find_anomalies' in service,
        'Deteccao de recorrencias registrada': 'def _find_recurring' in service,
        'Sem migration nova': '20260724_0004' in migration_test,
    }

    failed = False
    for label, ok in checks.items():
        print(f"[{'OK' if ok else 'ERROR'}] {label}.")
        failed = failed or not ok

    if failed:
        return 1
    print('[OK] Batch 15 validado.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
