from fastapi import (
    APIRouter,
    Depends,
    Path,
)

from app.api.dependencies import get_container
from app.api.schemas.budget import (
    BudgetOverviewResponse,
    BudgetPlanRequest,
)
from app.container import Container
from app.services.budget_service import BudgetOverview
from app.domain.billing_cycle import add_months


router = APIRouter(
    prefix="/budgets",
    tags=["budgets"],
)


def serialize_budget(
    overview: BudgetOverview,
) -> BudgetOverviewResponse:
    return BudgetOverviewResponse(
        year=overview.year,
        month=overview.month,
        configured=overview.configured,
        monthly_income=overview.monthly_income,
        reserve_target=overview.reserve_target,
        spending_limit=overview.spending_limit,
        spent=overview.spent,
        remaining=overview.remaining,
        available_after_reserve=(
            overview.available_after_reserve
        ),
        daily_limit=overview.daily_limit,
        usage_percent=overview.usage_percent,
        remaining_days=overview.remaining_days,
        status=overview.status,
    )


@router.get(
    "/{year}/{month}",
    response_model=BudgetOverviewResponse,
)
def get_budget(
    year: int = Path(
        ge=2000,
        le=2100,
    ),
    month: int = Path(
        ge=1,
        le=12,
    ),
    container: Container = Depends(
        get_container
    ),
) -> BudgetOverviewResponse:
    overview = (
        container.budget_service
        .get_overview(
            year=year,
            month=month,
        )
    )

    return serialize_budget(
        overview
    )


@router.put(
    "/{year}/{month}",
    response_model=BudgetOverviewResponse,
)
def save_budget(
    payload: BudgetPlanRequest,
    year: int = Path(
        ge=2000,
        le=2100,
    ),
    month: int = Path(
        ge=1,
        le=12,
    ),
    container: Container = Depends(
        get_container
    ),
) -> BudgetOverviewResponse:
    overview = None
    for offset in range(payload.repeat_months):
        target_year, target_month = add_months(year, month, offset)
        saved = container.budget_service.save_plan(
            year=target_year,
            month=target_month,
            monthly_income=payload.monthly_income,
            reserve_target=payload.reserve_target,
            spending_limit=payload.spending_limit,
        )
        if offset == 0:
            overview = saved

    if overview is None:
        raise RuntimeError("Nao foi possivel salvar o planejamento.")
    return serialize_budget(overview)
