import ast
from pathlib import Path


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    return found


def _assert_without(
    roots: tuple[str, ...],
    forbidden: tuple[str, ...],
) -> None:
    violations: list[str] = []
    for root in roots:
        for path in Path(root).rglob("*.py"):
            for imported in _imports(path):
                if imported.startswith(forbidden):
                    violations.append(f"{path}: {imported}")
    assert not violations, (
        "Dependencias proibidas:\n" + "\n".join(violations)
    )


def test_interfaces_do_not_access_database():
    _assert_without(
        ("app/api/routes", "app/bot/handlers"),
        ("app.repositories", "app.database"),
    )


def test_domain_is_framework_independent():
    _assert_without(
        ("app/domain",),
        (
            "app.api",
            "app.bot",
            "app.database",
            "app.repositories",
            "fastapi",
            "telegram",
            "sqlalchemy",
        ),
    )


def test_agent_only_calls_application_layer():
    _assert_without(
        ("app/agents",),
        ("app.database", "app.repositories", "sqlalchemy"),
    )
