import pytest

from app.repositories.expense_repository import (
    ExpenseRepository,
)


class ScalarResultStub:
    def all(self):
        return []


class SessionStub:
    def __init__(self):
        self.statements = []

    def scalars(self, statement):
        self.statements.append(statement)
        return ScalarResultStub()

    def get(self, model, entity_id):
        return None


def test_list_recent_applies_limit():
    session = SessionStub()
    repository = ExpenseRepository(
        session
    )

    repository.list_recent(
        limit=5
    )

    statement = session.statements[-1]
    compiled = statement.compile()

    assert compiled.params[
        "param_1"
    ] == 5


@pytest.mark.parametrize(
    "invalid_limit",
    [
        0,
        -1,
        True,
        "5",
    ],
)
def test_list_recent_rejects_invalid_limit(
    invalid_limit,
):
    repository = ExpenseRepository(
        SessionStub()
    )

    with pytest.raises(ValueError):
        repository.list_recent(
            limit=invalid_limit
        )


def test_current_month_adds_date_filter():
    session = SessionStub()
    repository = ExpenseRepository(
        session
    )

    repository.get_current_month(
        month=7,
        year=2026,
    )

    statement = session.statements[-1]
    sql = str(statement)

    assert "WHERE" in sql
    assert ">=" in sql
    assert "<" in sql


@pytest.mark.parametrize(
    ("month", "year"),
    [
        (0, 2026),
        (13, 2026),
        (True, 2026),
        (7, 0),
        (7, True),
    ],
)
def test_current_month_rejects_invalid_period(
    month,
    year,
):
    repository = ExpenseRepository(
        SessionStub()
    )

    with pytest.raises(ValueError):
        repository.get_current_month(
            month=month,
            year=year,
        )
