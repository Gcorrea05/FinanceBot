from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from app.api.dependencies import get_container
from app.api.schemas.report import (
    CategoryReportResponse,
    InstallmentReportResponse,
    MerchantReportResponse,
    MonthlyReportResponse,
    ReportOverviewResponse,
    ReportPeriodResponse,
)
from app.container import Container
from app.services.report_service import (
    MonthlyReportPoint,
    ReportOverview,
)


router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)


def serialize_month(
    item: MonthlyReportPoint,
) -> MonthlyReportResponse:
    return MonthlyReportResponse(
        year=item.year,
        month=item.month,
        label=item.label,
        total=item.total,
    )


def serialize_report(
    report: ReportOverview,
) -> ReportOverviewResponse:
    return ReportOverviewResponse(
        period=ReportPeriodResponse(
            start_year=(
                report.period.start_year
            ),
            start_month=(
                report.period.start_month
            ),
            end_year=(
                report.period.end_year
            ),
            end_month=(
                report.period.end_month
            ),
        ),
        total_spent=report.total_spent,
        monthly_average=(
            report.monthly_average
        ),
        transactions=report.transactions,
        highest_month=(
            serialize_month(
                report.highest_month
            )
            if report.highest_month
            is not None
            else None
        ),
        installment_commitment=(
            report.installment_commitment
        ),
        monthly=[
            serialize_month(item)
            for item in report.monthly
        ],
        categories=[
            CategoryReportResponse(
                name=item.name,
                total=item.total,
                percentage=(
                    item.percentage
                ),
            )
            for item in report.categories
        ],
        merchants=[
            MerchantReportResponse(
                name=item.name,
                total=item.total,
                transactions=(
                    item.transactions
                ),
            )
            for item in report.merchants
        ],
        installments=[
            InstallmentReportResponse(
                expense_id=(
                    item.expense_id
                ),
                purchase_place=(
                    item.purchase_place
                ),
                category=item.category,
                payment_method=(
                    item.payment_method
                ),
                purchase_value=(
                    item.purchase_value
                ),
                owner_total=(
                    item.owner_total
                ),
                total_installments=(
                    item.total_installments
                ),
                paid_installments=(
                    item.paid_installments
                ),
                pending_installments=(
                    item.pending_installments
                ),
                next_due_date=(
                    item.next_due_date
                ),
                remaining_amount=(
                    item.remaining_amount
                ),
            )
            for item in report.installments
        ],
    )


@router.get(
    "/overview",
    response_model=ReportOverviewResponse,
)
def get_report_overview(
    start_year: int = Query(
        ge=2000,
        le=2100,
    ),
    start_month: int = Query(
        ge=1,
        le=12,
    ),
    end_year: int = Query(
        ge=2000,
        le=2100,
    ),
    end_month: int = Query(
        ge=1,
        le=12,
    ),
    category: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),
    payment_method: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),
    place: str | None = Query(
        default=None,
        min_length=1,
        max_length=255,
    ),
    container: Container = Depends(
        get_container
    ),
) -> ReportOverviewResponse:
    try:
        report = (
            container.report_service
            .get_overview(
                start_year=start_year,
                start_month=start_month,
                end_year=end_year,
                end_month=end_month,
                category=category,
                payment_method=(
                    payment_method
                ),
                place=place,
            )
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    return serialize_report(
        report
    )
