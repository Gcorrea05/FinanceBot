import pytest

from app.repositories.base_repository import (
    BaseRepository,
)


class FakeSession:
    def __init__(
        self,
        fail_commit: bool = False,
    ):
        self.fail_commit = fail_commit
        self.added = None
        self.deleted = None
        self.committed = False
        self.refreshed = False
        self.rolled_back = False

    def add(self, entity):
        self.added = entity

    def delete(self, entity):
        self.deleted = entity

    def commit(self):
        if self.fail_commit:
            raise RuntimeError(
                "database error"
            )

        self.committed = True

    def refresh(self, entity):
        self.refreshed = True

    def rollback(self):
        self.rolled_back = True


def test_add_commits_and_refreshes_entity():
    session = FakeSession()
    repository = BaseRepository(session)
    entity = object()

    result = repository.add(entity)

    assert result is entity
    assert session.added is entity
    assert session.committed is True
    assert session.refreshed is True
    assert session.rolled_back is False


def test_add_rolls_back_when_commit_fails():
    session = FakeSession(
        fail_commit=True
    )

    repository = BaseRepository(session)

    with pytest.raises(
        RuntimeError,
        match="database error",
    ):
        repository.add(object())

    assert session.rolled_back is True
    assert session.refreshed is False
