from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import select

from app.container import Container
from app.database.models import Expense, ExpenseInstallment
from app.database.seed import seed_database
from app.database.session import get_session
from app.domain.billing_cycle import add_months, clipped_date


INVOICE_YEAR = 2026
INVOICE_MONTH = 8
INVOICE_DUE_DATE = date(2026, 8, 26)

INSTALLMENTS = (
    {
        "key": "unidentified-5-6",
        "description": "Compra parcelada (identificar)",
        "current": 5,
        "total": 6,
        "amount": Decimal("291.50"),
        "category": "Outros",
    },
    {
        "key": "vivara-2-3",
        "description": "Vivara",
        "current": 2,
        "total": 3,
        "amount": Decimal("73.33"),
        "category": "Compras",
    },
    {
        "key": "pedagoflix-4-10",
        "description": "Pedagoflix",
        "current": 4,
        "total": 10,
        "amount": Decimal("35.88"),
        "category": "Educação",
    },
    {
        "key": "rr-gutierrez-7-7",
        "description": "RR Gutierrez",
        "current": 7,
        "total": 7,
        "amount": Decimal("219.78"),
        "category": "Outros",
    },
    {
        "key": "youcom-3-5",
        "description": "Youcom",
        "current": 3,
        "total": 5,
        "amount": Decimal("93.94"),
        "category": "Vestuário",
    },
    {
        "key": "tablet-2-10",
        "description": "Tablet",
        "current": 2,
        "total": 10,
        "amount": Decimal("189.90"),
        "category": "Eletrônicos",
    },
    {
        "key": "amazon-4-5",
        "description": "Amazon",
        "current": 4,
        "total": 5,
        "amount": Decimal("35.58"),
        "category": "Compras",
    },
    {
        "key": "invoice-financing-1-3",
        "description": "Parcelamento de fatura",
        "current": 1,
        "total": 3,
        "amount": Decimal("455.77"),
        "category": "Financeiro",
    },
)

RECURRING = (
    {
        "key": "batch17-allianz",
        "description": "Allianz",
        "amount": Decimal("390.00"),
        "category": "Seguros",
        "due_day": 28,
        "start_date": date(2026, 7, 28),
    },
    {
        "key": "batch17-smartfit",
        "description": "Smart Fit",
        "amount": Decimal("149.90"),
        "category": "Saúde",
        "due_day": 2,
        "start_date": date(2026, 8, 2),
    },
)


def _marker(key: str) -> str:
    return f"[batch17:invoice-2026-08:{key}]"


def _expense_exists(session, key: str) -> bool:
    return (
        session.scalar(
            select(Expense.id).where(Expense.notes.like(f"%{_marker(key)}%"))
        )
        is not None
    )


def _seed_installment(container: Container, item: dict) -> bool:
    session = container.session
    if _expense_exists(session, item["key"]):
        return False

    category = container.lookup_service.get_category(item["category"])
    payment = container.lookup_service.get_payment_method("Cartão de crédito")
    total_installments = int(item["total"])
    current_installment = int(item["current"])
    installment_amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
    purchase_total = (installment_amount * total_installments).quantize(
        Decimal("0.01")
    )

    first_year, first_month = add_months(
        INVOICE_DUE_DATE.year,
        INVOICE_DUE_DATE.month,
        -(current_installment - 1),
    )
    first_due = clipped_date(first_year, first_month, 26)
    purchase_year, purchase_month = add_months(first_year, first_month, -1)

    expense = Expense(
        purchase_date=datetime(purchase_year, purchase_month, 27, 12, 0),
        purchase_place=item["description"],
        purchase_value=purchase_total,
        category_id=category.id,
        payment_method_id=payment.id,
        is_installment=True,
        is_shared=False,
        notes=(
            f"{_marker(item['key'])} Carga inicial da fatura 08/2026. "
            "Datas anteriores foram reconstruídas pela parcela atual informada."
        ),
    )

    installments: list[ExpenseInstallment] = []
    for number in range(1, total_installments + 1):
        due_year, due_month = add_months(first_year, first_month, number - 1)
        due_date = clipped_date(due_year, due_month, 26)
        is_paid = number < current_installment
        installments.append(
            ExpenseInstallment(
                installment_number=number,
                total_installments=total_installments,
                due_date=due_date,
                installment_value=installment_amount,
                is_paid=is_paid,
                paid_at=(
                    datetime.combine(due_date, datetime.min.time())
                    if is_paid
                    else None
                ),
            )
        )
    expense.installments = installments
    session.add(expense)
    return True


def _seed_recurring(container: Container, item: dict) -> bool:
    existing = container.recurring_expense_repository.get_by_source_key(item["key"])
    if existing is not None:
        return False
    category = container.lookup_service.get_category(item["category"])
    payment = container.lookup_service.get_payment_method("Cartão de crédito")
    container.recurring_expense_service.create_recurring(
        description=item["description"],
        amount=item["amount"],
        category_id=category.id,
        payment_method_id=payment.id,
        due_day=item["due_day"],
        start_date=item["start_date"],
        source_key=item["key"],
    )
    return True


def seed() -> tuple[int, int, Decimal]:
    session = get_session()
    created_installments = 0
    created_recurring = 0
    try:
        seed_database(session)
        container = Container(session)
        container.financial_profile_repository.get_or_create_default()

        for item in INSTALLMENTS:
            if _seed_installment(container, item):
                created_installments += 1
        session.commit()

        for item in RECURRING:
            if _seed_recurring(container, item):
                created_recurring += 1

        container.recurring_expense_service.materialize(
            from_year=INVOICE_YEAR,
            from_month=INVOICE_MONTH,
            months=18,
        )
        # Somente ocorrencias ja vencidas viram despesas realizadas.
        # As demais continuam planejadas e entram normalmente na projecao.
        container.recurring_expense_service.post_due(as_of=date.today())

        current_total = sum(
            (Decimal(item["amount"]) for item in INSTALLMENTS),
            Decimal("0.00"),
        ) + sum(
            (Decimal(item["amount"]) for item in RECURRING),
            Decimal("0.00"),
        )
        return created_installments, created_recurring, current_total.quantize(
            Decimal("0.01")
        )
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def main() -> int:
    installments, recurring, total = seed()
    print(f"[OK] Parcelamentos novos: {installments}")
    print(f"[OK] Recorrencias novas: {recurring}")
    print(f"[OK] Fatura 08/2026 conferida: R$ {total}")
    if total != Decimal("1935.58"):
        print("[ERROR] O total da carga inicial nao confere.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
