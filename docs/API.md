# FinanceBot REST API

The REST API is the backend contract for the future web interface.
The Telegram bot remains focused on quick registration and operational
queries.

## Local development

Install dependencies:

```powershell
python -m pip install -r requirements-dev.txt
```

Bootstrap migration tracking:

```powershell
python -m scripts.bootstrap_migrations
```

Start the API:

```powershell
python -m uvicorn app.api.main:app --reload
```

Open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Liveness: `http://127.0.0.1:8000/api/v1/health/live`
- Readiness: `http://127.0.0.1:8000/api/v1/health/ready`

## Initial endpoints

- `GET /api/v1/references/categories`
- `GET /api/v1/references/payment-methods`
- `POST /api/v1/expenses`
- `GET /api/v1/expenses`
- `GET /api/v1/expenses/{expense_id}`
- `DELETE /api/v1/expenses/{expense_id}`
- `GET /api/v1/receivables`
- `GET /api/v1/receivables/people/{person_id}`
- `POST /api/v1/receivables/{receivable_id}/settle`

## Scope and security

This batch is for local development and binds to `127.0.0.1` by
default. Authentication is intentionally deferred until the interface
and deployment model are defined. Do not expose this API publicly yet.

## Migrations

The first Alembic revision is an empty baseline because the schema
already existed before migration tracking.

The bootstrap command:

1. creates and seeds a new database, then stamps the baseline;
2. validates and stamps an existing compatible database;
3. upgrades a database that already has Alembic tracking.

For future model changes:

```powershell
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Review every generated migration before committing it.
