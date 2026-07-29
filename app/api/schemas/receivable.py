from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ReceivablePersonSummaryResponse(
    BaseModel
):
    person_id: int
    person_name: str
    total: Decimal
    pending_count: int


class ReceivableSummaryResponse(BaseModel):
    people: list[
        ReceivablePersonSummaryResponse
    ]
    total_general: Decimal


class ReceivableItemResponse(BaseModel):
    receivable_id: int
    expense_id: int
    person_id: int
    person_name: str
    purchase_place: str
    purchase_date: datetime
    amount: Decimal


class SettledReceivableItemResponse(
    ReceivableItemResponse
):
    settled_at: datetime


class ReceivableDetailResponse(BaseModel):
    person_id: int
    person_name: str
    items: list[ReceivableItemResponse]
    total: Decimal


class ReceivableHistoryResponse(BaseModel):
    items: list[SettledReceivableItemResponse]


class ReceivableSettlementResponse(BaseModel):
    receivable_id: int
    is_settled: bool
    settled_at: datetime | None
