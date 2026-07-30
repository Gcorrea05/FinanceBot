# FinanceBot REST API

A API e o contrato do site. O Telegram registra gastos pelos mesmos services de dominio.

## Execucao local

```powershell
python -m scripts.production_bootstrap
python -m uvicorn app.api.main:app --reload
```

Endpoints de saude:

- `GET /api/v1/health/live`;
- `GET /api/v1/health/ready`.

## Grupos de endpoints

- `/api/v1/expenses`: consulta e manutencao de despesas;
- `/api/v1/receivables`: valores a receber;
- `/api/v1/budgets`: renda, reserva e limite por competencia;
- `/api/v1/future`: projecao dos proximos meses;
- `/api/v1/recurring-expenses`: recorrencias e ocorrencias;
- `/api/v1/reports`: relatorios e exportacoes;
- `/api/v1/intelligence`: inteligencia explicavel;
- `/api/v1/imports`: importacoes CSV, XLSX e OFX;
- `/api/v1/automations`: configuracoes do scheduler;
- `/api/v1/references`: categorias e meios de pagamento.

## Meios de pagamento

A referencia publica retorna somente:

- Cartao de credito;
- Debito;
- Pix;
- Dinheiro.

## Planejamento

`PUT /api/v1/budgets/{year}/{month}` aceita renda, reserva, limite e `repeat_months`. Cada competencia e persistida como registro independente para preservar historico.

## Futuro

A projecao combina parcelas, recorrencias, gastos realizados e planejamento mensal. Ela nao transforma ocorrencias futuras em despesas antes da data prevista.

## Migrations

```powershell
alembic upgrade head
python -m scripts.validate_database
```

A revisao esperada apos este batch e `20260729_0006`.
