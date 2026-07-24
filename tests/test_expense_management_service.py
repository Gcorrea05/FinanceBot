from types import SimpleNamespace

import pytest

from app.services.expense_management_service import (
    ExpenseManagementService,
    ExpenseNotFoundError,
)


class RepositoryStub:
    def __init__(self):
        self.items = [
            SimpleNamespace(id=1),
            SimpleNamespace(id=2),
        ]
        self.deleted_ids = []

    def list_filtered(self, **kwargs):
        self.last_list_kwargs = kwargs
        return self.items

    def count_filtered(self, **kwargs):
        self.last_count_kwargs = kwargs
        return 2

    def get_detailed_by_id(self, expense_id):
        return next(
            (
                item
                for item in self.items
                if item.id == expense_id
            ),
            None,
        )

    def delete_by_id(self, expense_id):
        if expense_id == 1:
            self.deleted_ids.append(
                expense_id
            )
            return True

        return False


def test_list_builds_page():
    repository = RepositoryStub()
    service = ExpenseManagementService(
        repository
    )

    page = service.list(
        limit=10,
        offset=5,
        month=7,
        year=2026,
    )

    assert page.items == repository.items
    assert page.total == 2
    assert page.limit == 10
    assert page.offset == 5


def test_get_raises_for_missing_expense():
    service = ExpenseManagementService(
        RepositoryStub()
    )

    with pytest.raises(
        ExpenseNotFoundError,
    ):
        service.get(999)


def test_delete_raises_for_missing_expense():
    service = ExpenseManagementService(
        RepositoryStub()
    )

    with pytest.raises(
        ExpenseNotFoundError,
    ):
        service.delete(999)
