from decimal import Decimal

from app.api.schemas.expense import (
    ExpenseResponse,
    InstallmentResponse,
    SharedPersonResponse,
)
from app.database.models import Expense


CENT = Decimal("0.01")


def money(value) -> Decimal:
    return Decimal(
        str(value)
    ).quantize(CENT)


def serialize_expense(
    expense: Expense,
) -> ExpenseResponse:
    shared_people = [
        SharedPersonResponse(
            receivable_id=item.id,
            person_id=item.person_id,
            person_name=item.person.name,
            amount=money(item.shared_value),
            is_settled=item.is_settled,
            settled_at=item.settled_at,
        )
        for item in expense.people
    ]

    shared_total = sum(
        (
            item.amount
            for item in shared_people
        ),
        start=Decimal("0.00"),
    )

    purchase_value = money(
        expense.purchase_value
    )

    return ExpenseResponse(
        id=expense.id,
        purchase_date=expense.purchase_date,
        purchase_place=expense.purchase_place,
        purchase_value=purchase_value,
        category=expense.category.name,
        payment_method=(
            expense.payment_method.name
        ),
        is_installment=expense.is_installment,
        is_shared=expense.is_shared,
        owner_amount=money(
            purchase_value - shared_total
        ),
        notes=expense.notes,
        created_at=expense.created_at,
        updated_at=expense.updated_at,
        installments=[
            InstallmentResponse(
                id=item.id,
                installment_number=(
                    item.installment_number
                ),
                total_installments=(
                    item.total_installments
                ),
                due_date=item.due_date,
                amount=money(
                    item.installment_value
                ),
                is_paid=item.is_paid,
                paid_at=item.paid_at,
            )
            for item in expense.installments
        ],
        shared_people=shared_people,
    )
