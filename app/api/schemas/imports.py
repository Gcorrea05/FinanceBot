from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


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
