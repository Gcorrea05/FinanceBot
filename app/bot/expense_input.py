from decimal import Decimal


def format_brl(value: Decimal) -> str:
    normalized = Decimal(str(value)).quantize(Decimal("0.01"))
    raw = f"{normalized:,.2f}"
    return "R$ " + raw.replace(",", "#").replace(".", ",").replace("#", ".")
