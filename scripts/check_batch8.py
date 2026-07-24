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


def get_openapi_paths(application) -> set[str]:
    schema = application.openapi()

    return set(
        schema.get("paths", {}).keys()
    )


def main() -> int:
    application = create_app()

    actual_routes = get_openapi_paths(
        application
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

    if application.docs_url != "/docs":
        print(
            "[ERROR] Swagger documentation "
            "is not configured at /docs."
        )

        return 1

    configuration = Config(
        "alembic.ini"
    )

    script = ScriptDirectory.from_config(
        configuration
    )

    heads = script.get_heads()

    if heads != ["20260724_0001"]:
        print(
            "[ERROR] Unexpected migration heads: "
            f"{heads}"
        )

        return 1

    print(
        "[OK] REST API routes registered."
    )

    print(
        "[OK] Swagger documentation configured."
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
