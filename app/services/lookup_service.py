
from collections.abc import Iterable
from difflib import get_close_matches
from typing import Protocol, TypeVar, cast

from app.database.models import Category, PaymentMethod
from app.repositories.category_repository import CategoryRepository
from app.repositories.payment_method_repository import PaymentMethodRepository
from app.utils.text_normalizer import TextNormalizer


class LookupNotFoundError(ValueError):
    """Erro gerado quando um dado de refer?ncia n\u00e3o ? encontrado."""


class NamedEntity(Protocol):
    name: str


NamedEntityT = TypeVar("NamedEntityT", bound=NamedEntity)


class LookupService:
    """Resolve categorias e formas de pagamento a partir de texto livre."""

    CATEGORY_ALIASES: dict[str, str] = {
        # Alimenta??o
        "comida": "alimentacao",
        "restaurante": "alimentacao",
        "lanche": "alimentacao",
        "delivery": "alimentacao",
        "ifood": "alimentacao",

        # Mercado
        "supermercado": "mercado",
        "feira": "mercado",
        "hortifruti": "mercado",
        "compras do mes": "mercado",

        # Transporte
        "uber": "transporte",
        "99": "transporte",
        "taxi": "transporte",
        "onibus": "transporte",
        "metro": "transporte",
        "combustivel": "transporte",
        "gasolina": "transporte",

        # Sa?de
        "farmacia": "saude",
        "medico": "saude",
        "consulta": "saude",
        "remedio": "saude",

        # Educa??o
        "curso": "educacao",
        "faculdade": "educacao",
        "escola": "educacao",
        "livro": "educacao",

        # Assinaturas
        "assinatura": "assinaturas",
        "streaming": "assinaturas",
        "netflix": "assinaturas",
        "spotify": "assinaturas",

        # Casa
        "moradia": "casa",
        "aluguel": "casa",
        "condominio": "casa",
        "energia": "casa",
        "agua": "casa",

        # Lazer
        "cinema": "lazer",
        "passeio": "lazer",
        "entretenimento": "lazer",

        # Viagem
        "hotel": "viagem",
        "passagem": "viagem",
        "hospedagem": "viagem",

        # Outros
        "outro": "outros",
        "diversos": "outros",
    }

    PAYMENT_METHOD_ALIASES: dict[str, str] = {
        # Pix
        "transferencia pix": "pix",

        # D?bito
        "cartao de debito": "debito",
        "cartao debito": "debito",
        "deb": "debito",
        "cd": "debito",

        # Cr?dito
        "cartao de credito": "credito",
        "cartao credito": "credito",
        "cred": "credito",
        "cc": "credito",

        # Dinheiro
        "especie": "dinheiro",
        "cash": "dinheiro",
    }

    def __init__(
        self,
        category_repository: CategoryRepository,
        payment_method_repository: PaymentMethodRepository,
    ):
        self.category_repository = category_repository
        self.payment_method_repository = payment_method_repository

    def get_category(self, name: str) -> Category:
        category = self._resolve(
            raw_name=name,
            items=self.category_repository.get_all(),
            aliases=self.CATEGORY_ALIASES,
            entity_label="Categoria",
        )

        return cast(Category, category)

    def get_payment_method(self, name: str) -> PaymentMethod:
        payment_method = self._resolve(
            raw_name=name,
            items=self.payment_method_repository.get_all(),
            aliases=self.PAYMENT_METHOD_ALIASES,
            entity_label="Forma de pagamento",
        )

        return cast(PaymentMethod, payment_method)

    def list_category_names(self) -> list[str]:
        categories = self.category_repository.get_all()

        return sorted(
            (category.name for category in categories),
            key=TextNormalizer.normalize,
        )

    def list_payment_method_names(self) -> list[str]:
        payment_methods = self.payment_method_repository.get_all()

        return sorted(
            (payment.name for payment in payment_methods),
            key=TextNormalizer.normalize,
        )

    @staticmethod
    def _resolve(
        raw_name: str,
        items: Iterable[NamedEntityT],
        aliases: dict[str, str],
        entity_label: str,
    ) -> NamedEntityT:
        normalized_input = TextNormalizer.normalize(raw_name)

        if not normalized_input:
            raise LookupNotFoundError(
                f"{entity_label} n\u00e3o pode ficar vazia."
            )

        normalized_target = aliases.get(
            normalized_input,
            normalized_input,
        )

        item_index = {
            TextNormalizer.normalize(item.name): item
            for item in items
        }

        matched_item = item_index.get(normalized_target)

        if matched_item is not None:
            return matched_item

        suggestions = get_close_matches(
            normalized_target,
            list(item_index.keys()),
            n=3,
            cutoff=0.55,
        )

        message = (
            f"{entity_label} '{raw_name}' n\u00e3o encontrada."
        )

        if suggestions:
            suggested_names = [
                item_index[suggestion].name
                for suggestion in suggestions
            ]

            message += (
                " Voc\u00ea quis dizer: "
                + ", ".join(suggested_names)
                + "?"
            )

        raise LookupNotFoundError(message)
