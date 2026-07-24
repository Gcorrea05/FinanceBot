from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class ReportPeriodResponse(BaseModel):
    start_year: int
    start_month: int
    end_year: int
    end_month: int


class MonthlyReportResponse(BaseModel):
    year: int
    month: int
    label: str
    total: Decimal


class CategoryReportResponse(BaseModel):
    name: str
    total: Decimal
    percentage: Decimal


class MerchantReportResponse(BaseModel):
    name: str
    total: Decimal
    transactions: int


class InstallmentReportResponse(BaseModel):
    expense_id: int
    purchase_place: str
    category: str
    payment_method: str
    purchase_value: Decimal
    owner_total: Decimal
    total_installments: int
    paid_installments: int
    pending_installments: int
    next_due_date: date | None
    remaining_amount: Decimal


class ReportOverviewResponse(BaseModel):
    period: ReportPeriodResponse
    total_spent: Decimal
    monthly_average: Decimal
    transactions: int
    highest_month: MonthlyReportResponse | None
    installment_commitment: Decimal
    monthly: list[MonthlyReportResponse]
    categories: list[CategoryReportResponse]
    merchants: list[MerchantReportResponse]
    installments: list[InstallmentReportResponse]
