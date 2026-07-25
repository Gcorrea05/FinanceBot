from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class IntelligenceSummaryResponse(BaseModel):
    current_total: Decimal
    forecast_total: Decimal
    historical_average: Decimal
    trend_percent: Decimal | None
    installment_commitment: Decimal
    budget_usage_percent: Decimal | None
    budget_status: str
    data_months: int


class IntelligenceMonthlyResponse(BaseModel):
    year: int
    month: int
    label: str
    total: Decimal


class IntelligenceInsightResponse(BaseModel):
    code: str
    kind: str
    severity: str
    title: str
    message: str
    recommendation: str


class IntelligenceAnomalyResponse(BaseModel):
    expense_id: int
    purchase_date: date
    purchase_place: str
    category: str
    amount: Decimal
    category_median: Decimal
    difference_percent: Decimal


class IntelligenceRecurringResponse(BaseModel):
    purchase_place: str
    category: str
    occurrences: int
    average_amount: Decimal
    last_purchase_date: date
    expected_next_date: date


class IntelligenceOverviewResponse(BaseModel):
    year: int
    month: int
    generated_at: datetime
    summary: IntelligenceSummaryResponse
    monthly: list[IntelligenceMonthlyResponse]
    insights: list[IntelligenceInsightResponse]
    anomalies: list[IntelligenceAnomalyResponse]
    recurring: list[IntelligenceRecurringResponse]
