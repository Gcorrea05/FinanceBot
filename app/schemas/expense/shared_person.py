from dataclasses import dataclass

from app.domain.money import MoneyInput


@dataclass(frozen=True)
class SharedPersonCreate:
    name: str
    amount: MoneyInput | None = None
