from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ImportColumnMappingRequest(BaseModel):
    sheet_name: str | None = None
    header_row: int | None = Field(default=1, ge=1)
    data_start_row: int = Field(ge=1)
    date_column: int = Field(ge=0)
    description_columns: list[int] = Field(min_length=1, max_length=3)
    amount_column: int = Field(ge=0)
    external_id_column: int | None = Field(default=None, ge=0)
    date_format: Literal["auto", "dmy", "mdy", "ymd"] = "auto"
    decimal_separator: Literal["auto", "comma", "dot"] = "auto"
    amount_mode: Literal["all", "positive", "negative"] = "all"

    @field_validator("description_columns")
    @classmethod
    def validate_description_columns(cls, value: list[int]) -> list[int]:
        if any(column < 0 for column in value):
            raise ValueError("As colunas de descricao devem ser maiores ou iguais a zero.")
        if len(set(value)) != len(value):
            raise ValueError("As colunas de descricao nao podem se repetir.")
        return value


class ImportInspectionResponse(BaseModel):
    source_type: str
    sheets: list[str] = Field(default_factory=list)
    selected_sheet: str | None
    total_rows: int
    max_columns: int
    rows: list[list[str]] = Field(default_factory=list)
    mapping_required: bool


class ImportRowResponse(BaseModel):
    id: int
    row_number: int
    purchase_date: datetime | None
    purchase_place: str | None
    purchase_value: Decimal | None
    external_id: str | None
    status: str
    error_message: str | None
    expense_id: int | None


class ImportBatchResponse(BaseModel):
    id: int
    filename: str
    source_type: str
    status: str
    default_category: str
    default_payment_method: str
    total_rows: int
    ready_rows: int
    duplicate_rows: int
    invalid_rows: int
    imported_rows: int
    created_at: datetime
    completed_at: datetime | None
    rows: list[ImportRowResponse] = Field(default_factory=list)


class ImportHistoryResponse(BaseModel):
    items: list[ImportBatchResponse]
