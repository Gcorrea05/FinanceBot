from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from app.domain.billing_cycle import competence_for_charge
from app.domain.natural_expense_parser import NaturalExpenseParser
from app.domain.shared_expense import SharedExpenseSplitter

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = NaturalExpenseParser()
    installment = parser.parse("tablet 1700 parcelado em 10x")
    if installment.total != Decimal("1700.00") or installment.installments != 10:
        raise RuntimeError("Parser de parcelamento invalido.")

    shared = parser.parse("Presente Giron, 300, Tomas, Yuzo, minha parte 100")
    split = SharedExpenseSplitter().split(
        total=shared.total,
        people=shared.shared_people,
        owner_amount=shared.owner_amount,
    )
    if split.owner_amount != Decimal("100.00"):
        raise RuntimeError("Minha parte nao foi preservada.")
    if sum((item.amount for item in split.allocations), Decimal("0.00")) != Decimal("200.00"):
        raise RuntimeError("Divisao compartilhada invalida.")

    competence = competence_for_charge(
        charge_date=__import__("datetime").date(2026, 7, 28),
        payment_method_name="Cartão de crédito",
        cycle_start_day=27,
    )
    if competence != (2026, 8):
        raise RuntimeError("Ciclo do cartao invalido.")

    compose = (ROOT / "compose.yml").read_text(encoding="utf-8")
    if "scripts.production_bootstrap" not in compose:
        raise RuntimeError("Bootstrap de producao ausente do Compose.")

    print("[OK] Parser natural, divisao, ciclo e Compose validados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
