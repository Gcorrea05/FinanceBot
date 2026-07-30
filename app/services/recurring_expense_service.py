from datetime import date, datetime
from decimal import Decimal

from app.database.models import (
    Expense,
    ExpenseInstallment,
    RecurringExpense,
    RecurringExpenseOccurrence,
)
from app.domain.billing_cycle import (
    add_months,
    charge_date_for_competence,
    clipped_date,
    is_credit_card,
)
from app.repositories.financial_profile_repository import FinancialProfileRepository
from app.repositories.recurring_expense_repository import RecurringExpenseRepository


class RecurringExpenseService:
    def __init__(
        self,
        *,
        repository: RecurringExpenseRepository,
        profile_repository: FinancialProfileRepository,
    ):
        self.repository = repository
        self.profile_repository = profile_repository
        self.session = repository.session

    def create_recurring(
        self,
        *,
        description: str,
        amount,
        category_id: int,
        payment_method_id: int,
        due_day: int,
        start_date: date,
        source_key: str | None = None,
        active: bool = True,
        auto_post: bool = True,
    ) -> RecurringExpense:
        if source_key:
            existing = self.repository.get_by_source_key(source_key)
            if existing is not None:
                return existing
        item = RecurringExpense(
            description=" ".join(description.split()),
            amount=Decimal(str(amount)).quantize(Decimal("0.01")),
            category_id=category_id,
            payment_method_id=payment_method_id,
            due_day=due_day,
            start_date=start_date,
            active=active,
            auto_post=auto_post,
            source_key=source_key,
        )
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item


    def update_recurring(
        self,
        recurring: RecurringExpense,
        *,
        amount,
        due_day: int,
        active: bool,
        auto_post: bool,
    ) -> RecurringExpense:
        if not 1 <= due_day <= 31:
            raise ValueError("O dia deve estar entre 1 e 31.")
        resolved_amount = Decimal(str(amount)).quantize(Decimal("0.01"))
        if resolved_amount <= 0:
            raise ValueError("O valor deve ser maior que zero.")
        profile = self.profile_repository.get_or_create_default()
        recurring.amount = resolved_amount
        recurring.due_day = due_day
        recurring.active = active
        recurring.auto_post = auto_post
        for occurrence in recurring.occurrences:
            if occurrence.status != "planned":
                continue
            occurrence.amount = resolved_amount
            occurrence.due_date = charge_date_for_competence(
                year=occurrence.competence_year,
                month=occurrence.competence_month,
                due_day=due_day,
                payment_method_name=recurring.payment_method.name,
                cycle_start_day=profile.credit_card_cycle_start_day,
            )
        self.session.commit()
        self.session.refresh(recurring)
        return recurring

    def materialize(
        self,
        *,
        from_year: int | None = None,
        from_month: int | None = None,
        months: int | None = None,
        today: date | None = None,
    ) -> int:
        current = today or date.today()
        start_year = from_year or current.year
        start_month = from_month or current.month
        profile = self.profile_repository.get_or_create_default()
        horizon = months or profile.projection_months
        created = 0

        for recurring in self.repository.list_active():
            for offset in range(horizon):
                year, month = add_months(start_year, start_month, offset)
                if self.repository.get_occurrence(recurring.id, year, month):
                    continue
                due_date = charge_date_for_competence(
                    year=year,
                    month=month,
                    due_day=recurring.due_day,
                    payment_method_name=recurring.payment_method.name,
                    cycle_start_day=profile.credit_card_cycle_start_day,
                )
                if due_date < recurring.start_date:
                    continue
                if recurring.end_date is not None and due_date > recurring.end_date:
                    continue
                self.session.add(
                    RecurringExpenseOccurrence(
                        recurring_expense_id=recurring.id,
                        competence_year=year,
                        competence_month=month,
                        due_date=due_date,
                        amount=Decimal(str(recurring.amount)).quantize(Decimal("0.01")),
                        status="planned",
                    )
                )
                created += 1
        self.session.commit()
        return created

    def post_due(self, *, as_of: date | None = None) -> int:
        target = as_of or date.today()
        profile = self.profile_repository.get_or_create_default()
        posted = 0
        for occurrence in self.repository.list_due(target):
            recurring = occurrence.recurring_expense
            credit = is_credit_card(recurring.payment_method.name)
            expense = Expense(
                purchase_date=datetime.combine(occurrence.due_date, datetime.min.time()),
                purchase_place=recurring.description,
                purchase_value=occurrence.amount,
                category_id=recurring.category_id,
                payment_method_id=recurring.payment_method_id,
                is_installment=credit,
                is_shared=False,
                notes=f"Gerada automaticamente da recorrencia #{recurring.id}.",
            )
            if credit:
                expense.installments = [
                    ExpenseInstallment(
                        installment_number=1,
                        total_installments=1,
                        due_date=clipped_date(
                            occurrence.competence_year,
                            occurrence.competence_month,
                            profile.credit_card_installment_day,
                        ),
                        installment_value=occurrence.amount,
                    )
                ]
            self.session.add(expense)
            self.session.flush()
            occurrence.expense_id = expense.id
            occurrence.status = "posted"
            occurrence.posted_at = datetime.utcnow()
            posted += 1
        self.session.commit()
        return posted
