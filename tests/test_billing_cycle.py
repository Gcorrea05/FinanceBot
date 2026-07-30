from datetime import date

from app.domain.billing_cycle import charge_date_for_competence, competence_for_charge, first_installment_date


def test_charge_on_day_28_belongs_to_next_invoice_competence():
    assert competence_for_charge(
        charge_date=date(2026, 7, 28),
        payment_method_name="Cartão de crédito",
        cycle_start_day=27,
    ) == (2026, 8)


def test_august_invoice_charge_date_for_allianz_is_july_28():
    assert charge_date_for_competence(
        year=2026,
        month=8,
        due_day=28,
        payment_method_name="Cartão de crédito",
        cycle_start_day=27,
    ) == date(2026, 7, 28)


def test_installment_due_date_uses_day_26():
    assert first_installment_date(
        purchase_date=date(2026, 7, 27),
        closing_day=26,
        installment_day=26,
    ) == date(2026, 8, 26)
