from decimal import Decimal
from io import BytesIO

from openpyxl import Workbook

from app.imports.parser import parse_import_file


def test_parse_csv_and_detect_duplicate_fingerprint_shape():
    content = (
        "data;descricao;valor;id\n"
        "24/07/2026;Mercado Central;123,45;abc-1\n"
    ).encode("utf-8")
    parsed = parse_import_file("extrato.csv", content)
    row = parsed.rows[0]
    assert parsed.source_type == "csv"
    assert row.purchase_place == "Mercado Central"
    assert row.purchase_value == Decimal("123.45")
    assert len(row.fingerprint or "") == 64


def test_parse_xlsx():
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Data", "Descricao", "Valor"])
    sheet.append(["2026-07-24", "Farmacia", 80.50])
    stream = BytesIO()
    workbook.save(stream)
    parsed = parse_import_file("extrato.xlsx", stream.getvalue())
    assert parsed.rows[0].purchase_value == Decimal("80.50")


def test_parse_ofx():
    content = b"""
    <OFX><BANKTRANLIST><STMTTRN>
    <DTPOSTED>20260724120000
    <TRNAMT>-42.90
    <FITID>tx-10
    <NAME>Padaria
    </STMTTRN></BANKTRANLIST></OFX>
    """
    parsed = parse_import_file("conta.ofx", content)
    assert parsed.rows[0].purchase_place == "Padaria"
    assert parsed.rows[0].purchase_value == Decimal("42.90")
