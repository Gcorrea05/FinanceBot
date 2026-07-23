from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import PaymentMethod
from app.repositories.base_repository import BaseRepository


class PaymentMethodRepository(BaseRepository[PaymentMethod]):

    def __init__(self, session: Session):
        super().__init__(session)

    def get_all(self):
        return self.session.scalars(
            select(PaymentMethod)
        ).all()

    def get_by_id(self, payment_method_id: int):
        return self.session.get(
            PaymentMethod,
            payment_method_id
        )

    def get_by_name(self, name: str):
        return self.session.scalar(
            select(PaymentMethod)
            .where(PaymentMethod.name.ilike(name))
        )