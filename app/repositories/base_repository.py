from typing import Generic, TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):

    def __init__(self, session: Session):
        self.session = session

    def add(self, entity: T):
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def delete(self, entity: T):
        self.session.delete(entity)
        self.session.commit()

    def update(self):
        self.session.commit()