from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_container
from app.api.schemas.intelligence import (
    IntelligenceAnomalyResponse,
    IntelligenceInsightResponse,
    IntelligenceMonthlyResponse,
    IntelligenceOverviewResponse,
    IntelligenceRecurringResponse,
    IntelligenceSummaryResponse,
)
from app.container import Container


router = APIRouter(prefix='/intelligence', tags=['intelligence'])


@router.get('/overview', response_model=IntelligenceOverviewResponse)
def get_intelligence_overview(
    year: int | None = Query(default=None, ge=2000, le=2100),
    month: int | None = Query(default=None, ge=1, le=12),
    container: Container = Depends(get_container),
) -> IntelligenceOverviewResponse:
    today = date.today()
    selected_year = year or today.year
    selected_month = month or today.month

    try:
        overview = container.intelligence_service.get_overview(
            year=selected_year,
            month=selected_month,
            today=today,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return IntelligenceOverviewResponse(
        year=overview.year,
        month=overview.month,
        generated_at=overview.generated_at,
        summary=IntelligenceSummaryResponse(**overview.summary.__dict__),
        monthly=[IntelligenceMonthlyResponse(**item.__dict__) for item in overview.monthly],
        insights=[IntelligenceInsightResponse(**item.__dict__) for item in overview.insights],
        anomalies=[IntelligenceAnomalyResponse(**item.__dict__) for item in overview.anomalies],
        recurring=[IntelligenceRecurringResponse(**item.__dict__) for item in overview.recurring],
    )
