import calendar
from datetime import date


def add_months(year: int, month: int, offset: int) -> tuple[int, int]:
    index = year * 12 + (month - 1) + offset
    return index // 12, index % 12 + 1


def clipped_date(year: int, month: int, day: int) -> date:
    return date(year, month, min(day, calendar.monthrange(year, month)[1]))


def is_credit_card(payment_method_name: str) -> bool:
    normalized = payment_method_name.casefold()
    return "credito" in normalized or "crédito" in normalized


def charge_date_for_competence(
    *,
    year: int,
    month: int,
    due_day: int,
    payment_method_name: str,
    cycle_start_day: int,
) -> date:
    if is_credit_card(payment_method_name) and due_day >= cycle_start_day:
        year, month = add_months(year, month, -1)
    return clipped_date(year, month, due_day)


def competence_for_charge(
    *,
    charge_date: date,
    payment_method_name: str,
    cycle_start_day: int,
) -> tuple[int, int]:
    if is_credit_card(payment_method_name) and charge_date.day >= cycle_start_day:
        return add_months(charge_date.year, charge_date.month, 1)
    return charge_date.year, charge_date.month


def first_installment_date(
    *,
    purchase_date: date,
    closing_day: int,
    installment_day: int,
) -> date:
    year, month = purchase_date.year, purchase_date.month
    if purchase_date.day > closing_day:
        year, month = add_months(year, month, 1)
    return clipped_date(year, month, installment_day)
