from fastapi import APIRouter

from app.api.routes.automations import router as automations_router
from app.api.routes.budgets import router as budgets_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.expenses import router as expenses_router
from app.api.routes.exports import router as exports_router
from app.api.routes.future import router as future_router
from app.api.routes.health import router as health_router
from app.api.routes.imports import router as imports_router
from app.api.routes.intelligence import router as intelligence_router
from app.api.routes.receivables import router as receivables_router
from app.api.routes.recurring import router as recurring_router
from app.api.routes.references import router as references_router
from app.api.routes.reports import router as reports_router

api_router = APIRouter()
for router in (
    health_router,
    references_router,
    expenses_router,
    exports_router,
    receivables_router,
    budgets_router,
    dashboard_router,
    future_router,
    recurring_router,
    reports_router,
    imports_router,
    intelligence_router,
    automations_router,
):
    api_router.include_router(router)

__all__ = ["api_router"]
