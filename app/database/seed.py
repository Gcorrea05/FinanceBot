from sqlalchemy import delete, func, select

from app.constants import DEFAULT_SHARED_PEOPLE
from app.database.models import Category, Expense, PaymentMethod, Person
from app.utils.text_normalizer import TextNormalizer


CATEGORY_NAMES: tuple[str, ...] = (
    "Alimentação",
    "Mercado",
    "Transporte",
    "Saúde",
    "Lazer",
    "Educação",
    "Assinaturas",
    "Casa",
    "Viagem",
    "Compras",
    "Vestuário",
    "Eletrônicos",
    "Seguros",
    "Financeiro",
    "Outros",
)

PAYMENT_METHOD_NAMES: tuple[str, ...] = (
    "Cartão de crédito",
    "Débito",
    "Pix",
    "Dinheiro",
)

PAYMENT_ALIASES: dict[str, str] = {
    "credito": "Cartão de crédito",
    "cartao credito": "Cartão de crédito",
    "cartao de credito": "Cartão de crédito",
    "debito": "Débito",
    "cartao debito": "Débito",
    "cartao de debito": "Débito",
    "pix": "Pix",
    "dinheiro": "Dinheiro",
}


def seed_database(session) -> None:
    try:
        _normalize_payment_methods(session)
        _seed_categories(session)
        _seed_payment_methods(session)
        _seed_default_people(session)
        session.commit()
    except Exception:
        session.rollback()
        raise


def _seed_categories(session) -> None:
    existing = {
        TextNormalizer.normalize(name): name
        for name in session.scalars(select(Category.name)).all()
    }
    for name in CATEGORY_NAMES:
        if TextNormalizer.normalize(name) not in existing:
            session.add(Category(name=name))


def _seed_payment_methods(session) -> None:
    existing = {
        TextNormalizer.normalize(name)
        for name in session.scalars(select(PaymentMethod.name)).all()
    }
    for name in PAYMENT_METHOD_NAMES:
        if TextNormalizer.normalize(name) not in existing:
            session.add(PaymentMethod(name=name))


def _normalize_payment_methods(session) -> None:
    methods = list(session.scalars(select(PaymentMethod)).all())
    by_target: dict[str, PaymentMethod] = {}

    for method in methods:
        normalized = TextNormalizer.normalize(method.name)
        target = PAYMENT_ALIASES.get(normalized)
        if target is None:
            continue
        target_key = TextNormalizer.normalize(target)
        canonical = by_target.get(target_key)
        if canonical is None:
            canonical = next(
                (
                    item
                    for item in methods
                    if TextNormalizer.normalize(item.name) == target_key
                ),
                None,
            )
        if canonical is None:
            method.name = target
            by_target[target_key] = method
            continue
        if canonical.id == method.id:
            canonical.name = target
            by_target[target_key] = canonical
            continue
        session.query(Expense).filter(
            Expense.payment_method_id == method.id
        ).update({Expense.payment_method_id: canonical.id})
        session.delete(method)
        canonical.name = target
        by_target[target_key] = canonical


def _seed_default_people(session) -> None:
    existing = set(session.scalars(select(Person.normalized_name)).all())
    for name in DEFAULT_SHARED_PEOPLE:
        normalized_name = TextNormalizer.normalize(name)
        if normalized_name in existing:
            continue
        session.add(Person(name=name, normalized_name=normalized_name, active=True))
        existing.add(normalized_name)
