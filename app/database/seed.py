from sqlalchemy import select

from app.constants import DEFAULT_SHARED_PEOPLE
from app.database.models import (
    Category,
    PaymentMethod,
    Person,
)
from app.utils.text_normalizer import TextNormalizer


CATEGORY_NAMES: tuple[str, ...] = (
    "Alimenta\u00e7\u00e3o",
    "Mercado",
    "Transporte",
    "Sa\u00fade",
    "Lazer",
    "Educa\u00e7\u00e3o",
    "Assinaturas",
    "Casa",
    "Viagem",
    "Outros",
)

PAYMENT_METHOD_NAMES: tuple[str, ...] = (
    "Pix",
    "D\u00e9bito",
    "Cr\u00e9dito",
    "Dinheiro",
)


def seed_database(session) -> None:
    try:
        _seed_categories(session)
        _seed_payment_methods(session)
        _seed_default_people(session)
        session.commit()

    except Exception:
        session.rollback()
        raise


def _seed_categories(session) -> None:
    existing = set(
        session.scalars(
            select(Category.name)
        ).all()
    )

    for name in CATEGORY_NAMES:
        if name not in existing:
            session.add(
                Category(name=name)
            )


def _seed_payment_methods(session) -> None:
    existing = set(
        session.scalars(
            select(PaymentMethod.name)
        ).all()
    )

    for name in PAYMENT_METHOD_NAMES:
        if name not in existing:
            session.add(
                PaymentMethod(name=name)
            )


def _seed_default_people(session) -> None:
    existing = set(
        session.scalars(
            select(Person.normalized_name)
        ).all()
    )

    for name in DEFAULT_SHARED_PEOPLE:
        normalized_name = TextNormalizer.normalize(
            name
        )

        if normalized_name in existing:
            continue

        session.add(
            Person(
                name=name,
                normalized_name=normalized_name,
                active=True,
            )
        )

        existing.add(normalized_name)
