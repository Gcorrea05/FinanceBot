from datetime import datetime
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database.base import Base
from app.database.models import (
    Category,
    Expense,
    ExpensePerson,
    PaymentMethod,
    Person,
)
from app.repositories.receivable_repository import (
    ReceivableRepository,
)


def test_summary_details_and_settlement():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:"
    )

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        category = Category(
            name="Mercado"
        )
        payment = PaymentMethod(
            name="Pix"
        )
        person = Person(
            name="Tomas",
            normalized_name="tomas",
        )

        expense = Expense(
            purchase_date=datetime(
                2026,
                7,
                23,
            ),
            purchase_place="Mercado Central",
            purchase_value=100.00,
            category=category,
            payment_method=payment,
            is_installment=False,
            is_shared=True,
        )

        receivable = ExpensePerson(
            expense=expense,
            person=person,
            shared_value=Decimal("70.00"),
        )

        session.add(receivable)
        session.commit()

        repository = ReceivableRepository(
            session
        )

        summary = (
            repository.list_open_summary()
        )

        assert summary[0].person_name == "Tomas"
        assert Decimal(
            str(summary[0].total)
        ) == Decimal("70.00")

        details = (
            repository.list_open_for_person(
                person.id
            )
        )

        assert len(details) == 1
        assert (
            details[0].purchase_place
            == "Mercado Central"
        )

        repository.settle(
            receivable.id
        )

        assert (
            repository.list_open_summary()
            == []
        )
