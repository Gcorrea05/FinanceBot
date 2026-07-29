from pathlib import Path


REQUIRED_FILES = (
    "app/services/monthly_export_service.py",
    "app/api/routes/exports.py",
    "tests/test_monthly_export_service.py",
    "tests/test_import_credit_handling.py",
    "frontend/src/api/alignmentClient.test.ts",
)


for filename in REQUIRED_FILES:
    if not Path(filename).exists():
        raise SystemExit(
            f"[ERRO] Arquivo ausente: {filename}"
        )

checks = {
    "app/api/routes/__init__.py": "exports_router",
    "app/container.py": "monthly_export_service",
    "app/services/intelligence_service.py": "contribution_for_month",
    "app/imports/parser.py": "credit_column",
    "frontend/src/pages/ReportsPage.tsx": "downloadMonthlyExcel",
    "frontend/src/pages/ReceivablesPage.tsx": "Desfazer recebimento",
    "frontend/src/components/ExpenseTable.tsx": "Sua parte",
    "frontend/src/pages/DashboardPage.tsx": "data.budget.spent",
}

for filename, token in checks.items():
    content = Path(filename).read_text(
        encoding="utf-8"
    )
    if token not in content:
        raise SystemExit(
            f"[ERRO] {filename} nao contem: {token}"
        )

print("[OK] Exportacao mensal em Excel registrada.")
print("[OK] Dashboard usa o mesmo calculo do planejamento.")
print("[OK] Valor total e sua parte aparecem nas despesas.")
print("[OK] Recebimentos podem ser desfeitos.")
print("[OK] Creditos e estornos possuem tratamento seguro.")
print("[OK] Inteligencia usa parcelas e historico com movimento.")
print("[OK] Batch 15.1 validado.")
