from alembic.config import Config
from alembic.script import ScriptDirectory

from app.api.app import create_app


EXPECTED_ROUTES = {
    "/api/v1/health/live",
    "/api/v1/health/ready",
    "/api/v1/references/categories",
    "/api/v1/references/payment-methods",
    "/api/v1/expenses",
    "/api/v1/expenses/{expense_id}",
    "/api/v1/receivables",
    "/api/v1/receivables/people/{person_id}",
    (
        "/api/v1/receivables/"
        "{receivable_id}/settle"
    ),
}


def main() -> int:
    application = create_app()
    schema = application.openapi()
    actual_routes = set(
        schema.get("paths", {}).keys()
    )

    missing = sorted(
        EXPECTED_ROUTES
        - actual_routes
    )

    if missing:
        print(
            "[ERROR] Missing API routes:"
        )

        for route in missing:
            print(f"  - {route}")

        return 1

    configuration = Config(
        "alembic.ini"
    )

    script = ScriptDirectory.from_config(
        configuration
    )

    revisions = {
        revision.revision
        for revision in script.walk_revisions()
    }

    if "20260724_0001" not in revisions:
        print(
            "[ERROR] Alembic baseline is missing."
        )
        return 1

    if len(script.get_heads()) != 1:
        print(
            "[ERROR] Multiple migration heads found: "
            f"{script.get_heads()}"
        )
        return 1

    print(
        "[OK] REST API routes registered."
    )
    print(
        "[OK] Alembic baseline configured."
    )
    print(
        "[OK] Batch 8 validated."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
