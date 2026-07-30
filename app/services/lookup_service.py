from collections.abc import Iterable
from difflib import get_close_matches
from typing import Protocol, TypeVar, cast

from app.database.models import Category, PaymentMethod
from app.repositories.category_repository import CategoryRepository
from app.repositories.payment_method_repository import PaymentMethodRepository
from app.utils.text_normalizer import TextNormalizer


class LookupNotFoundError(ValueError):
    """Raised when a reference value cannot be resolved."""


class NamedEntity(Protocol):
    name: str


NamedEntityT = TypeVar("NamedEntityT", bound=NamedEntity)


class LookupService:
    CATEGORY_ALIASES: dict[str, str] = {
        "comida": "alimentacao",
        "restaurante": "alimentacao",
        "lanche": "alimentacao",
        "delivery": "alimentacao",
        "ifood": "alimentacao",
        "supermercado": "mercado",
        "feira": "mercado",
        "hortifruti": "mercado",
        "compras do mes": "mercado",
        "uber": "transporte",
        "99": "transporte",
        "taxi": "transporte",
        "onibus": "transporte",
        "metro": "transporte",
        "combustivel": "transporte",
        "gasolina": "transporte",
        "farmacia": "saude",
        "medico": "saude",
        "consulta": "saude",
        "remedio": "saude",
        "curso": "educacao",
        "faculdade": "educacao",
        "escola": "educacao",
        "livro": "educacao",
        "assinatura": "assinaturas",
        "streaming": "assinaturas",
        "netflix": "assinaturas",
        "spotify": "assinaturas",
        "moradia": "casa",
        "aluguel": "casa",
        "condominio": "casa",
        "energia": "casa",
        "agua": "casa",
        "cinema": "lazer",
        "passeio": "lazer",
        "entretenimento": "lazer",
        "hotel": "viagem",
        "passagem": "viagem",
        "hospedagem": "viagem",
        "outro": "outros",
        "diversos": "outros",
    }

    ALLOWED_PAYMENT_METHODS: tuple[str, ...] = (
        "Cartão de crédito",
        "Débito",
        "Pix",
        "Dinheiro",
    )

    PAYMENT_METHOD_ALIASES: dict[str, str] = {
        "credito": "cartao de credito",
        "cartao credito": "cartao de credito",
        "cc": "cartao de credito",
        "debito": "debito",
        "cartao de debito": "debito",
        "cartao debito": "debito",
        "deb": "debito",
        "cd": "debito",
        "transferencia pix": "pix",
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
        return cast(
            Category,
            self._resolve(
                name,
                self.category_repository.get_all(),
                self.CATEGORY_ALIASES,
                "Categoria",
            ),
        )

    def get_payment_method(self, name: str) -> PaymentMethod:
        return cast(
            PaymentMethod,
            self._resolve(
                name,
                self.payment_method_repository.get_all(),
                self.PAYMENT_METHOD_ALIASES,
                "Forma de pagamento",
            ),
        )

    def list_category_names(self) -> list[str]:
        return sorted(
            (item.name for item in self.category_repository.get_all()),
            key=TextNormalizer.normalize,
        )

    def list_payment_method_names(self) -> list[str]:
        available: set[str] = set()

        for item in self.payment_method_repository.get_all():
            normalized = TextNormalizer.normalize(item.name)
            canonical = self.PAYMENT_METHOD_ALIASES.get(
                normalized,
                normalized,
            )
            available.add(canonical)

        return [
            name
            for name in self.ALLOWED_PAYMENT_METHODS
            if TextNormalizer.normalize(name) in available
        ]

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
                f"{entity_label} nao pode ficar vazia."
            )

        target = aliases.get(
            normalized_input,
            normalized_input,
        )
        index: dict[str, NamedEntityT] = {}

        for item in items:
            normalized_name = TextNormalizer.normalize(
                item.name
            )
            canonical_name = aliases.get(
                normalized_name,
                normalized_name,
            )
            index.setdefault(normalized_name, item)
            index.setdefault(canonical_name, item)

        matched = index.get(target)
        if matched is not None:
            return matched

        suggestions = get_close_matches(
            target,
            list(index),
            n=3,
            cutoff=0.55,
        )
        message = f"{entity_label} '{raw_name}' nao encontrada."
        if suggestions:
            names = []
            for suggestion in suggestions:
                candidate = index[suggestion].name
                if candidate not in names:
                    names.append(candidate)
            message += " Voce quis dizer: " + ", ".join(names) + "?"

        raise LookupNotFoundError(message)
