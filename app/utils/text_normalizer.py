
import re
import unicodedata


class TextNormalizer:
    """Padroniza textos recebidos pelos servi?os da aplica??o."""

    _NON_ALPHANUMERIC = re.compile(r"[^a-z0-9\s]")
    _WHITESPACE = re.compile(r"\s+")

    @classmethod
    def normalize(cls, value: str) -> str:
        if not isinstance(value, str):
            raise TypeError("O valor informado para normaliza??o deve ser uma string.")

        decomposed = unicodedata.normalize("NFKD", value)

        without_accents = "".join(
            character
            for character in decomposed
            if not unicodedata.combining(character)
        )

        normalized = without_accents.casefold()
        normalized = normalized.replace("_", " ")
        normalized = normalized.replace("-", " ")
        normalized = cls._NON_ALPHANUMERIC.sub(" ", normalized)
        normalized = cls._WHITESPACE.sub(" ", normalized)

        return normalized.strip()
