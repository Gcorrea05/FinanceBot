from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Category
from app.repositories.base_repository import BaseRepository


class CategoryRepository(BaseRepository[Category]):

    def __init__(self, session: Session):
        super().__init__(session)

    def get_all(self):
        return self.session.scalars(
            select(Category)
        ).all()

    def get_by_id(self, category_id: int):
        return self.session.get(Category, category_id)

    def get_by_name(self, name: str):
        return self.session.scalar(
            select(Category)
            .where(Category.name.ilike(name))
        )