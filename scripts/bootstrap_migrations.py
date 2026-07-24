import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.database import models as _models
from app.database.base import Base
from app.database.seed import seed_database
from app.database.session import (
    create_database,
    engine,
    get_session,
)


del _models


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

BASELINE_REVISION = "20260724_0001"


def alembic_config() -> Config:
    return Config(
        str(
            PROJECT_ROOT
            / "alembic.ini"
        )
    )


def schema_differences(
    *,
    excluded_tables: set[str] | None = None,
) -> list[str]:
    inspector = inspect(engine)

    actual_tables = set(
        inspector.get_table_names()
    )

    excluded = excluded_tables or set()

    expected_tables = {
        table.name: {
            column.name
            for column in table.columns
        }
        for table in Base.metadata.sorted_tables
        if table.name not in excluded
    }

    differences: list[str] = []

    for table_name, expected_columns in (
        expected_tables.items()
    ):
        if table_name not in actual_tables:
            differences.append(
                f"Missing table: {table_name}"
            )
            continue

        actual_columns = {
            column["name"]
            for column in inspector.get_columns(
                table_name
            )
        }

        missing_columns = sorted(
            expected_columns
            - actual_columns
        )

        if missing_columns:
            differences.append(
                (
                    f"Missing columns in "
                    f"{table_name}: "
                    f"{missing_columns}"
                )
            )

    return differences


def seed_current_database() -> None:
    session = get_session()

    try:
        seed_database(session)

    finally:
        session.close()


def bootstrap() -> str:
    inspector = inspect(engine)

    application_tables = {
        table
        for table in inspector.get_table_names()
        if table != "alembic_version"
    }

    configuration = alembic_config()

    if not application_tables:
        create_database()
        seed_current_database()

        command.stamp(
            configuration,
            "head",
        )

        return (
            "Database created and stamped "
            "at migration head."
        )

    current_tables = set(
        inspector.get_table_names()
    )

    if "alembic_version" not in current_tables:
        differences = schema_differences(
            excluded_tables={
                "budgets",
            }
        )

        if differences:
            formatted = "\n".join(
                f"  - {item}"
                for item in differences
            )

            raise RuntimeError(
                (
                    "The existing pre-migration "
                    "database is not compatible "
                    "with the baseline:\n"
                    f"{formatted}"
                )
            )

        command.stamp(
            configuration,
            BASELINE_REVISION,
        )

    command.upgrade(
        configuration,
        "head",
    )

    differences = schema_differences()

    if differences:
        formatted = "\n".join(
            f"  - {item}"
            for item in differences
        )

        raise RuntimeError(
            (
                "The upgraded database is not "
                "compatible with the current "
                "models:\n"
                f"{formatted}"
            )
        )

    seed_current_database()

    return (
        "Existing database upgraded to "
        "migration head."
    )


def main() -> int:
    try:
        result = bootstrap()

    except Exception as error:
        print(f"[ERROR] {error}")
        return 1

    print(f"[OK] {result}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
