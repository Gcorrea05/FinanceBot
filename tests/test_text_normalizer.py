
import pytest

from app.utils.text_normalizer import TextNormalizer


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("Alimenta\u00e7\u00e3o", "alimentacao"),
        ("  Cart\u00e3o   de CR\u00c9DITO  ", "cartao de credito"),
        ("PIX", "pix"),
        ("casa-e-jardim", "casa e jardim"),
        ("  99 / Uber  ", "99 uber"),
    ],
)
def test_normalize_text(raw_value: str, expected: str):
    assert TextNormalizer.normalize(raw_value) == expected


def test_normalize_empty_text():
    assert TextNormalizer.normalize("   ") == ""
