from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from io import BytesIO, StringIO
from pathlib import Path
import re
import unicodedata


MAX_IMPORT_ROWS = 5000


class ImportFileError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedImportRow:
    row_number: int
    purchase_date: datetime | None
    purchase_place: str | None
    purchase_value: Decimal | None
    external_id: str | None
    fingerprint: str | None
    error_message: str | None = None

    @property
    def valid(self) -> bool:
        return self.error_message is None


@dataclass(frozen=True)
class ParsedImportFile:
    source_type: str
    rows: tuple[ParsedImportRow, ...]


DATE_ALIASES = {"date", "data", "purchase_date", "data_compra", "dtposted"}
PLACE_ALIASES = {
    "description", "descricao", "historico", "estabelecimento", "local",
    "purchase_place", "name", "memo",
}
AMOUNT_ALIASES = {"amount", "valor", "value", "purchase_value", "trnamt"}
ID_ALIASES = {"id", "external_id", "fitid", "documento", "transaction_id"}


def _normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _clean_text(value: object) -> str:
    return " ".join(str(value or "").strip().split())


def _pick(mapping: dict[str, object], aliases: set[str]) -> object | None:
    for key, value in mapping.items():
        if _normalize(key) in aliases:
            return value
    return None


def _parse_date(value: object) -> datetime:
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())

    text = _clean_text(value)
    if not text:
        raise ValueError("Data ausente.")

    iso_candidate = text.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(iso_candidate)
        return parsed.replace(tzinfo=None)
    except ValueError:
        pass

    for pattern in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%y"):
        try:
            return datetime.strptime(text[:10], pattern)
        except ValueError:
            continue

    if re.fullmatch(r"\d{8}.*", text):
        try:
            return datetime.strptime(text[:8], "%Y%m%d")
        except ValueError:
            pass

    raise ValueError(f"Data invalida: {text}")


def _parse_amount(value: object) -> Decimal:
    if isinstance(value, Decimal):
        amount = value
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        amount = Decimal(str(value))
    else:
        text = _clean_text(value)
        if not text:
            raise ValueError("Valor ausente.")

        negative = text.startswith("(") and text.endswith(")")
        text = text.replace("R$", "").replace("$", "").replace(" ", "")
        text = text.strip("()")

        if "," in text and "." in text:
            if text.rfind(",") > text.rfind("."):
                text = text.replace(".", "").replace(",", ".")
            else:
                text = text.replace(",", "")
        elif "," in text:
            text = text.replace(".", "").replace(",", ".")

        try:
            amount = Decimal(text)
        except InvalidOperation as error:
            raise ValueError(f"Valor invalido: {value}") from error

        if negative:
            amount = -amount

    amount = abs(amount).quantize(Decimal("0.01"))
    if amount <= 0:
        raise ValueError("O valor deve ser maior que zero.")
    return amount


def _fingerprint(source_type: str, transaction_date: datetime, place: str, amount: Decimal, external_id: str | None) -> str:
    raw = "|".join(
        (
            source_type,
            transaction_date.date().isoformat(),
            f"{amount:.2f}",
            _normalize(place),
            _normalize(external_id or ""),
        )
    )
    return sha256(raw.encode("utf-8")).hexdigest()


def _row_from_mapping(row_number: int, mapping: dict[str, object], source_type: str) -> ParsedImportRow:
    try:
        transaction_date = _parse_date(_pick(mapping, DATE_ALIASES))
        place = _clean_text(_pick(mapping, PLACE_ALIASES))
        if not place:
            raise ValueError("Descricao ou estabelecimento ausente.")
        amount = _parse_amount(_pick(mapping, AMOUNT_ALIASES))
        external_value = _pick(mapping, ID_ALIASES)
        external_id = _clean_text(external_value) or None
        fingerprint = _fingerprint(source_type, transaction_date, place, amount, external_id)
        return ParsedImportRow(
            row_number=row_number,
            purchase_date=transaction_date,
            purchase_place=place[:255],
            purchase_value=amount,
            external_id=external_id,
            fingerprint=fingerprint,
        )
    except ValueError as error:
        return ParsedImportRow(
            row_number=row_number,
            purchase_date=None,
            purchase_place=_clean_text(_pick(mapping, PLACE_ALIASES))[:255] or None,
            purchase_value=None,
            external_id=None,
            fingerprint=None,
            error_message=str(error),
        )


def _validate_headers(headers: list[object]) -> None:
    normalized = {_normalize(header) for header in headers if header is not None}
    required = (
        (DATE_ALIASES, "data"),
        (PLACE_ALIASES, "descricao"),
        (AMOUNT_ALIASES, "valor"),
    )
    missing = [label for aliases, label in required if normalized.isdisjoint(aliases)]
    if missing:
        raise ImportFileError("Colunas obrigatorias ausentes: " + ", ".join(missing) + ".")


def _decode_csv(content: bytes) -> str:
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ImportFileError("Nao foi possivel identificar a codificacao do CSV.")


def _parse_csv(content: bytes) -> tuple[ParsedImportRow, ...]:
    text = _decode_csv(content)
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
        dialect.delimiter = ";"
    reader = csv.DictReader(StringIO(text), dialect=dialect)
    if not reader.fieldnames:
        raise ImportFileError("O CSV nao possui cabecalho.")
    _validate_headers(list(reader.fieldnames))
    rows = tuple(
        _row_from_mapping(index, dict(row), "csv")
        for index, row in enumerate(reader, start=2)
        if any(_clean_text(value) for value in row.values())
    )
    return rows


def _parse_xlsx(content: bytes) -> tuple[ParsedImportRow, ...]:
    try:
        from openpyxl import load_workbook
    except ImportError as error:
        raise ImportFileError("A dependencia openpyxl nao esta instalada.") from error

    try:
        workbook = load_workbook(BytesIO(content), read_only=True, data_only=True)
    except Exception as error:
        raise ImportFileError("O arquivo XLSX nao pode ser lido.") from error

    sheet = workbook.active
    iterator = sheet.iter_rows(values_only=True)
    try:
        headers = list(next(iterator))
    except StopIteration as error:
        raise ImportFileError("A planilha esta vazia.") from error

    _validate_headers(headers)
    rows: list[ParsedImportRow] = []
    for index, values in enumerate(iterator, start=2):
        if not any(_clean_text(value) for value in values):
            continue
        mapping = {str(header or ""): value for header, value in zip(headers, values)}
        rows.append(_row_from_mapping(index, mapping, "xlsx"))
    return tuple(rows)


def _ofx_value(block: str, tag: str) -> str:
    match = re.search(rf"<{tag}>([^<\r\n]+)", block, flags=re.IGNORECASE)
    return _clean_text(match.group(1)) if match else ""


def _parse_ofx(content: bytes) -> tuple[ParsedImportRow, ...]:
    text = _decode_csv(content)
    blocks = re.findall(r"<STMTTRN>(.*?)(?:</STMTTRN>|(?=<STMTTRN>)|$)", text, flags=re.IGNORECASE | re.DOTALL)
    if not blocks:
        raise ImportFileError("Nenhuma transacao STMTTRN foi encontrada no OFX.")

    rows: list[ParsedImportRow] = []
    for index, block in enumerate(blocks, start=1):
        mapping = {
            "dtposted": _ofx_value(block, "DTPOSTED"),
            "trnamt": _ofx_value(block, "TRNAMT"),
            "name": _ofx_value(block, "NAME") or _ofx_value(block, "MEMO"),
            "fitid": _ofx_value(block, "FITID"),
        }
        rows.append(_row_from_mapping(index, mapping, "ofx"))
    return tuple(rows)


def parse_import_file(filename: str, content: bytes) -> ParsedImportFile:
    if not content:
        raise ImportFileError("O arquivo esta vazio.")

    extension = Path(filename).suffix.lower().lstrip(".")
    parsers = {"csv": _parse_csv, "xlsx": _parse_xlsx, "ofx": _parse_ofx}
    parser = parsers.get(extension)
    if parser is None:
        raise ImportFileError("Formato nao suportado. Use CSV, XLSX ou OFX.")

    rows = parser(content)
    if not rows:
        raise ImportFileError("Nenhuma linha de transacao foi encontrada.")
    if len(rows) > MAX_IMPORT_ROWS:
        raise ImportFileError(f"O arquivo excede o limite de {MAX_IMPORT_ROWS} transacoes.")

    return ParsedImportFile(source_type=extension, rows=rows)
