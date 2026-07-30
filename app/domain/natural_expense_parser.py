from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal

from app.domain.money import MoneyParser
from app.schemas.expense.shared_person import SharedPersonCreate
from app.utils.text_normalizer import TextNormalizer


class NaturalExpenseParseError(ValueError):
    pass


@dataclass(frozen=True)
class NaturalExpenseDraft:
    description: str
    total: Decimal
    category: str
    installments: int = 1
    recurring_due_day: int | None = None
    shared_people: tuple[SharedPersonCreate, ...] = ()
    owner_amount: Decimal | None = None
    original_text: str = ""

    @property
    def is_installment(self) -> bool:
        return self.installments > 1

    @property
    def is_recurring(self) -> bool:
        return self.recurring_due_day is not None

    @property
    def is_shared(self) -> bool:
        return bool(self.shared_people)


class NaturalExpenseParser:
    """Parser deterministico para o formato curto usado no Telegram."""

    _INSTALLMENT = re.compile(
        r"\b(?:parcelad[oa]\s*(?:em)?\s*|em\s+)?(?P<count>\d{1,3})\s*x\b",
        re.IGNORECASE,
    )
    _RECURRING = re.compile(
        r"\b(?:todo\s+(?:mes|m[eê]s)\s*)?(?:todo\s+dia|mensal(?:mente)?(?:\s+dia)?)\s*(?P<day>\d{1,2})\b",
        re.IGNORECASE,
    )
    _MONEY = re.compile(
        r"(?<![\w])(?:R\$\s*)?(?P<value>\d+(?:\.\d{3})*(?:,\d{1,2})?|\d+(?:\.\d{1,2})?)(?![\w])",
        re.IGNORECASE,
    )
    _OWNER = re.compile(r"^(?:eu|minha\s+parte)\b", re.IGNORECASE)

    CATEGORY_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("Mercado", ("mercado", "supermercado", "feira", "hortifruti")),
        ("Alimentacao", ("restaurante", "ifood", "lanche", "comida", "delivery")),
        ("Transporte", ("uber", "taxi", "99", "gasolina", "combustivel", "metro", "onibus")),
        ("Saude", ("farmacia", "remedio", "medico", "consulta", "academia", "smart fit", "smartfit")),
        ("Educacao", ("curso", "faculdade", "escola", "livro", "pedagoflix")),
        ("Assinaturas", ("netflix", "spotify", "streaming", "assinatura")),
        ("Casa", ("aluguel", "condominio", "energia", "agua", "internet")),
        ("Vestuario", ("youcom", "roupa", "sapato", "tenis")),
        ("Eletronicos", ("tablet", "celular", "notebook", "computador")),
        ("Seguros", ("allianz", "seguro")),
        ("Financeiro", ("parcelamento de fatura", "juros", "tarifa")),
        ("Compras", ("amazon", "vivara", "presente", "compra")),
        ("Lazer", ("cinema", "passeio", "jogo", "viagem")),
    )

    def parse(self, text: str) -> NaturalExpenseDraft:
        raw = " ".join((text or "").strip().split())
        if not raw:
            raise NaturalExpenseParseError("Envie a descricao e o valor do gasto.")

        installment_match = self._INSTALLMENT.search(raw)
        recurring_match = self._RECURRING.search(raw)
        installments = int(installment_match.group("count")) if installment_match else 1
        if installments < 2 and installment_match:
            raise NaturalExpenseParseError("O parcelamento deve possuir pelo menos 2 parcelas.")
        if installments > 120:
            raise NaturalExpenseParseError("O parcelamento pode possuir no maximo 120 parcelas.")

        recurring_day = int(recurring_match.group("day")) if recurring_match else None
        if recurring_day is not None and not 1 <= recurring_day <= 31:
            raise NaturalExpenseParseError("O dia mensal deve estar entre 1 e 31.")
        if installment_match and recurring_match:
            raise NaturalExpenseParseError(
                "Escolha apenas um tipo: parcelamento ou gasto mensal recorrente."
            )

        clean_for_amount = raw
        for match in (installment_match, recurring_match):
            if match:
                clean_for_amount = clean_for_amount.replace(match.group(0), " ")

        parts = [part.strip() for part in raw.split(",") if part.strip()]
        amount_match = None
        if len(parts) >= 2:
            amount_match = self._MONEY.search(parts[1])

        if amount_match is not None:
            raw_amount = amount_match.group("value")
            description = parts[0]
            participant_parts = parts[2:]
        else:
            amount_match = self._MONEY.search(clean_for_amount)
            if amount_match is None:
                raise NaturalExpenseParseError(
                    "Nao encontrei o valor. Exemplo: mercado 230,50"
                )
            raw_amount = amount_match.group("value")
            description = clean_for_amount[: amount_match.start()].strip(" ,-;")
            participant_parts = []

        try:
            total = MoneyParser.parse(raw_amount)
        except ValueError as error:
            raise NaturalExpenseParseError(str(error)) from error

        description = self._clean_description(description)
        if len(description) < 2:
            raise NaturalExpenseParseError(
                "Informe uma descricao antes do valor. Exemplo: mercado 230"
            )

        people: list[SharedPersonCreate] = []
        owner_amount: Decimal | None = None
        seen: set[str] = set()
        for item in participant_parts:
            owner = self._OWNER.match(item)
            explicit_match = self._MONEY.search(item)
            explicit = None
            if explicit_match:
                try:
                    explicit = MoneyParser.parse(explicit_match.group("value"))
                except ValueError as error:
                    raise NaturalExpenseParseError(str(error)) from error

            if owner:
                if owner_amount is not None:
                    raise NaturalExpenseParseError("Minha parte foi informada mais de uma vez.")
                owner_amount = explicit
                continue

            name = item
            if explicit_match:
                name = (item[: explicit_match.start()] + item[explicit_match.end() :]).strip(" :-=")
            name = " ".join(name.split())
            if len(name) < 2:
                raise NaturalExpenseParseError("Informe um nome valido na divisao.")
            normalized = TextNormalizer.normalize(name)
            if normalized in seen:
                raise NaturalExpenseParseError(f"A pessoa '{name}' foi repetida.")
            seen.add(normalized)
            people.append(SharedPersonCreate(name=name.title(), amount=explicit))

        return NaturalExpenseDraft(
            description=description,
            total=total,
            category=self.infer_category(description),
            installments=installments,
            recurring_due_day=recurring_day,
            shared_people=tuple(people),
            owner_amount=owner_amount,
            original_text=raw,
        )

    @classmethod
    def infer_category(cls, description: str) -> str:
        normalized = TextNormalizer.normalize(description)
        for category, terms in cls.CATEGORY_RULES:
            if any(TextNormalizer.normalize(term) in normalized for term in terms):
                return category
        return "Outros"

    @staticmethod
    def _clean_description(value: str) -> str:
        cleaned = re.sub(r"\b(?:parcelad[oa]|mensal(?:mente)?|todo\s+dia|todo\s+mes)\b", " ", value, flags=re.IGNORECASE)
        cleaned = " ".join(cleaned.strip(" ,-;").split())
        return cleaned[:255]
