from decimal import Decimal
from io import BytesIO

from openpyxl import Workbook

from app.imports.parser import (
    ImportColumnMapping,
    inspect_import_file,
    parse_import_file,
)


def test_csv_accepts_arbitrary_headers_with_explicit_mapping():
    content = (
        "LANCAMENTO;NOME DA LOJA;TOTAL COBRADO;CODIGO\n"
        "24/07/2026;Mercado Central;123,45;abc-1\n"
    ).encode("utf-8")

    inspection = inspect_import_file("fatura.csv", content)
    assert inspection.rows[0][0] == "LANCAMENTO"
    assert inspection.mapping_required is True

    parsed = parse_import_file(
        "fatura.csv",
        content,
        ImportColumnMapping(
            data_start_row=2,
            date_column=0,
            description_columns=(1,),
            amount_column=2,
            external_id_column=3,
            date_format="dmy",
            decimal_separator="comma",
        ),
    )
    row = parsed.rows[0]
    assert row.purchase_place == "Mercado Central"
    assert row.purchase_value == Decimal("123.45")
    assert len(row.fingerprint or "") == 64


def test_csv_without_header_maps_by_column_position():
    content = "24/07/2026;Farmacia;80,50\n".encode("utf-8")
    parsed = parse_import_file(
        "sem-cabecalho.csv",
        content,
        ImportColumnMapping(
            data_start_row=1,
            date_column=0,
            description_columns=(1,),
            amount_column=2,
            date_format="dmy",
            decimal_separator="comma",
        ),
    )
    assert parsed.rows[0].purchase_value == Decimal("80.50")


def test_xlsx_uses_selected_sheet_and_arbitrary_columns():
    workbook = Workbook()
    ignored_sheet = workbook.active
    ignored_sheet.title = "Resumo"
    ignored_sheet.append(["Texto sem transacoes"])
    sheet = workbook.create_sheet("Fatura Julho")
    sheet.append(["Quando", "Detalhe", "Montante"])
    sheet.append(["2026-07-24", "Farmacia", 80.50])
    stream = BytesIO()
    workbook.save(stream)

    inspection = inspect_import_file(
        "fatura.xlsx",
        stream.getvalue(),
        sheet_name="Fatura Julho",
    )
    assert inspection.selected_sheet == "Fatura Julho"

    parsed = parse_import_file(
        "fatura.xlsx",
        stream.getvalue(),
        ImportColumnMapping(
            sheet_name="Fatura Julho",
            data_start_row=2,
            date_column=0,
            description_columns=(1,),
            amount_column=2,
            date_format="ymd",
        ),
    )
    assert parsed.rows[0].purchase_value == Decimal("80.50")


def test_amount_sign_rule_can_ignore_positive_rows():
    content = (
        "data;descricao;valor\n"
        "24/07/2026;Pagamento;100,00\n"
        "24/07/2026;Compra;-42,90\n"
    ).encode("utf-8")
    parsed = parse_import_file(
        "conta.csv",
        content,
        ImportColumnMapping(
            data_start_row=2,
            date_column=0,
            description_columns=(1,),
            amount_column=2,
            amount_mode="negative",
            date_format="dmy",
            decimal_separator="comma",
        ),
    )
    assert parsed.rows[0].ignored is True
    assert parsed.rows[1].purchase_value == Decimal("42.90")


def test_parse_ofx_remains_automatic():
    content = b"""
    <OFX><BANKTRANLIST><STMTTRN>
    <DTPOSTED>20260724120000
    <TRNAMT>-42.90
    <FITID>tx-10
    <NAME>Padaria
    </STMTTRN></BANKTRANLIST></OFX>
    """
    inspection = inspect_import_file("conta.ofx", content)
    assert inspection.mapping_required is False
    parsed = parse_import_file("conta.ofx", content)
    assert parsed.rows[0].purchase_place == "Padaria"
    assert parsed.rows[0].purchase_value == Decimal("42.90")
