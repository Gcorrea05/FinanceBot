from app.imports.parser import (
    ImportColumnMapping,
    parse_import_file,
)


def test_separate_debit_and_credit_columns_ignore_credits():
    content = (
        "Data;Descricao;Debito;Credito\n"
        "10/07/2026;Mercado;120,00;\n"
        "11/07/2026;Estorno;;35,00\n"
    ).encode("utf-8")
    mapping = ImportColumnMapping(
        data_start_row=2,
        date_column=0,
        description_columns=(1,),
        debit_column=2,
        credit_column=3,
        decimal_separator="comma",
        amount_mode="positive",
    )

    parsed = parse_import_file(
        "fatura.csv",
        content,
        mapping,
    )

    assert parsed.rows[0].valid is True
    assert str(parsed.rows[0].purchase_value) == "120.00"
    assert parsed.rows[1].ignored is True
    assert "Credito" in parsed.rows[1].error_message


def test_single_amount_column_ignores_opposite_sign():
    content = (
        "Data;Descricao;Valor\n"
        "10/07/2026;Compra;80,00\n"
        "11/07/2026;Estorno;-20,00\n"
    ).encode("utf-8")
    mapping = ImportColumnMapping(
        data_start_row=2,
        date_column=0,
        description_columns=(1,),
        amount_column=2,
        decimal_separator="comma",
        amount_mode="positive",
    )

    parsed = parse_import_file(
        "fatura.csv",
        content,
        mapping,
    )

    assert parsed.rows[0].valid is True
    assert parsed.rows[1].ignored is True
