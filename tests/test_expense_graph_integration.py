from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    create_engine,
    func,
    select,
)
from sqlalchemy.orm import Session

from app.database.base import Base
from app.database.models import (
    Category,
    Expense,
    ExpenseInstallment,
    ExpensePerson,
    PaymentMethod,
    Person,
)


def test_expense_graph_is_persisted_atomically():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
    )

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        category = Category(
            name="Viagem",
        )

        payment_method = PaymentMethod(
            name="Credito",
        )

        person = Person(
            name="Ana",
            normalized_name="ana",
        )

        expense = Expense(
            purchase_date=datetime(
                2026,
                7,
                24,
                10,
                0,
            ),
            purchase_place="Hotel Teste",
            purchase_value=1000.00,
            category=category,
            payment_method=payment_method,
            is_installment=True,
            is_shared=True,
        )

        expense.installments.append(
            ExpenseInstallment(
                installment_number=1,
                total_installments=2,
                due_date=date(
                    2026,
                    8,
                    10,
                ),
                installment_value=(
                    Decimal("500.00")
                ),
            )
        )

        expense.installments.append(
            ExpenseInstallment(
                installment_number=2,
                total_installments=2,
                due_date=date(
                    2026,
                    9,
                    10,
                ),
                installment_value=(
                    Decimal("500.00")
                ),
            )
        )

        expense.people.append(
            ExpensePerson(
                person=person,
                shared_value=(
                    Decimal("250.00")
                ),
            )
        )

        session.add(expense)
        session.commit()

        assert session.scalar(
            select(
                func.count(
                    ExpenseInstallment.id
                )
            )
        ) == 2

        assert session.scalar(
            select(
                func.count(
                    ExpensePerson.id
                )
            )
        ) == 1

        assert session.scalar(
            select(
                func.count(Person.id)
            )
        ) == 1
