from datetime import date, datetime, time
from decimal import Decimal

from app.domain.money import MoneyParser
from app.schemas.expense.shared_person import SharedPersonCreate
from app.utils.text_normalizer import TextNormalizer


class ExpenseInputError(ValueError):
    """Raised when a Telegram expense input cannot be parsed."""


def parse_date_input(
    value: str,
    *,
    today: date | None = None,
    purchase_date: date | None = None,
) -> date:
    reference_today = today or date.today()
    normalized = TextNormalizer.normalize(value)

    if normalized == "hoje":
        return reference_today

    if normalized in {
        "data da compra",
        "mesma data",
    }:
        if purchase_date is None:
            raise ExpenseInputError(
                "A data da compra ainda nao foi informada."
            )

        return purchase_date

    try:
        return datetime.strptime(
            value.strip(),
            "%d/%m/%Y",
        ).date()

    except ValueError as error:
        raise ExpenseInputError(
            "Informe a data no formato DD/MM/AAAA."
        ) from error


def parse_purchase_datetime(
    value: str,
    *,
    today: date | None = None,
) -> datetime:
    resolved_date = parse_date_input(
        value,
        today=today,
    )

    return datetime.combine(
        resolved_date,
        time.min,
    )


def parse_yes_no(value: str) -> bool:
    normalized = TextNormalizer.normalize(value)

    if normalized in {"sim", "s"}:
        return True

    if normalized in {"nao", "n"}:
        return False

    raise ExpenseInputError(
        "Responda Sim ou Nao."
    )


def parse_installment_count(value: str) -> int:
    normalized = value.strip()

    try:
        installments = int(normalized)

    except ValueError as error:
        raise ExpenseInputError(
            "Informe uma quantidade inteira de parcelas."
        ) from error

    if installments < 2:
        raise ExpenseInputError(
            "Informe pelo menos 2 parcelas."
        )

    if installments > 120:
        raise ExpenseInputError(
            "O limite e de 120 parcelas."
        )

    return installments


def parse_shared_mode(value: str) -> str:
    normalized = TextNormalizer.normalize(value)

    if normalized in {
        "divisao igual",
        "igual",
    }:
        return "equal"

    if normalized in {
        "valores exatos",
        "exato",
        "exatos",
    }:
        return "exact"

    raise ExpenseInputError(
        "Escolha Divisao igual ou Valores exatos."
    )


def parse_equal_people(
    value: str,
) -> tuple[SharedPersonCreate, ...]:
    names = [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]

    if not names:
        raise ExpenseInputError(
            "Informe pelo menos uma pessoa."
        )

    return tuple(
        SharedPersonCreate(name=name)
        for name in names
    )


def parse_exact_people(
    value: str,
) -> tuple[SharedPersonCreate, ...]:
    entries = [
        item.strip()
        for item in value.split(";")
        if item.strip()
    ]

    if not entries:
        raise ExpenseInputError(
            "Informe pelo menos uma pessoa e um valor."
        )

    people: list[SharedPersonCreate] = []

    for entry in entries:
        if "=" not in entry:
            raise ExpenseInputError(
                (
                    "Use o formato "
                    "Nome=valor; Nome=valor."
                )
            )

        name, raw_amount = entry.split(
            "=",
            maxsplit=1,
        )

        name = name.strip()
        raw_amount = raw_amount.strip()

        if not name:
            raise ExpenseInputError(
                "O nome da pessoa nao pode ficar vazio."
            )

        try:
            amount = MoneyParser.parse(
                raw_amount
            )

        except ValueError as error:
            raise ExpenseInputError(
                (
                    f"Valor invalido para "
                    f"'{name}': {error}"
                )
            ) from error

        people.append(
            SharedPersonCreate(
                name=name,
                amount=amount,
            )
        )

    return tuple(people)


def format_brl(value: Decimal) -> str:
    normalized = value.quantize(
        Decimal("0.01")
    )

    raw = f"{normalized:,.2f}"

    return (
        "R$ "
        + raw
        .replace(",", "#")
        .replace(".", ",")
        .replace("#", ".")
    )
