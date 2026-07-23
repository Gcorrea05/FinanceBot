from typing import Generic, TypeVar

from sqlalchemy.orm import Session


T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    def add(
        self,
        entity: T,
    ) -> T:
        self.session.add(entity)

        self._commit()

        self.session.refresh(entity)

        return entity

    def delete(
        self,
        entity: T,
    ) -> None:
        self.session.delete(entity)

        self._commit()

    def update(
        self,
        entity: T | None = None,
    ) -> T | None:
        if entity is not None:
            self.session.add(entity)

        self._commit()

        if entity is not None:
            self.session.refresh(entity)

        return entity

    def _commit(self) -> None:
        try:
            self.session.commit()

        except Exception:
            self.session.rollback()
            raise
