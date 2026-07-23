from app.database.models import Category
from app.database.models import PaymentMethod


def seed_database(session):

    if session.query(Category).count() == 0:

        categories = [
            "Alimentação",
            "Mercado",
            "Transporte",
            "Saúde",
            "Lazer",
            "Educação",
            "Assinaturas",
            "Casa",
            "Viagem",
            "Outros"
        ]

        for category in categories:
            session.add(Category(name=category))

    if session.query(PaymentMethod).count() == 0:

        methods = [
            "Pix",
            "Débito",
            "Crédito",
            "Dinheiro"
        ]

        for method in methods:
            session.add(PaymentMethod(name=method))

    session.commit()