import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from sqlalchemy import inspect

from app.database.session import engine


EXPECTED_COLUMNS = {
    "people": {
        "id",
        "name",
        "normalized_name",
        "active",
        "created_at",
        "updated_at",
    },
    "expense_installments": {
        "id",
        "expense_id",
        "installment_number",
        "total_installments",
        "due_date",
        "installment_value",
        "is_paid",
        "paid_at",
        "created_at",
    },
    "expense_people": {
        "id",
        "expense_id",
        "person_id",
        "shared_value",
        "is_settled",
        "settled_at",
        "created_at",
    },
}


def main() -> None:
    inspector = inspect(engine)
    tables = set(
        inspector.get_table_names()
    )

    errors: list[str] = []

    for table_name, expected in (
        EXPECTED_COLUMNS.items()
    ):
        if table_name not in tables:
            errors.append(
                f"Tabela ausente: {table_name}"
            )
            continue

        existing = {
            column["name"]
            for column in inspector.get_columns(
                table_name
            )
        }

        missing = expected - existing

        if missing:
            errors.append(
                (
                    f"Colunas ausentes em "
                    f"{table_name}: "
                    f"{sorted(missing)}"
                )
            )

    if errors:
        print(
            "[ERRO] O banco local usa um schema antigo."
        )

        for error in errors:
            print(f"  - {error}")

        raise SystemExit(1)

    print(
        "[OK] Schema local compativel com o Batch 4."
    )


if __name__ == "__main__":
    main()
