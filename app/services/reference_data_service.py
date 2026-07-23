from app.database.models import Category
from app.database.models import PaymentMethod
from app.repositories.category_repository import CategoryRepository
from app.repositories.payment_method_repository import (
    PaymentMethodRepository,
)


class ReferenceDataService:

    def __init__(
        self,
        category_repository: CategoryRepository,
        payment_method_repository: PaymentMethodRepository,
    ):
        self.category_repository = category_repository
        self.payment_method_repository = payment_method_repository

    # ------------------------
    # CATEGORY
    # ------------------------

    def get_category(self, name: str) -> Category:

        category = self.category_repository.get_by_name(name)

        if category is None:
            raise ValueError(
                f"Categoria '{name}' não encontrada."
            )

        return category

    # ------------------------
    # PAYMENT METHOD
    # ------------------------

    def get_payment_method(
        self,
        name: str,
    ) -> PaymentMethod:

        payment = self.payment_method_repository.get_by_name(
            name
        )

        if payment is None:
            raise ValueError(
                f"Forma de pagamento '{name}' não encontrada."
            )

        return payment