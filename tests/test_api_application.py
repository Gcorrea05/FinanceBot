from app.api.app import create_app


def get_openapi_paths(application) -> set[str]:
    schema = application.openapi()

    return set(
        schema.get("paths", {}).keys()
    )


def test_api_registers_expected_routes():
    application = create_app()

    paths = get_openapi_paths(application)

    expected_paths = {
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

    assert expected_paths.issubset(paths)
    assert application.docs_url == "/docs"
    assert application.redoc_url == "/redoc"


def test_api_has_no_telegram_routes():
    application = create_app()

    paths = get_openapi_paths(application)

    assert all(
        "telegram" not in path.lower()
        for path in paths
    )
