from fastapi import APIRouter

from app.api.routes.automations import router as automations_router
from app.api.routes.budgets import router as budgets_router
from app.api.routes.expenses import router as expenses_router
from app.api.routes.exports import router as exports_router
from app.api.routes.health import router as health_router
from app.api.routes.imports import router as imports_router
from app.api.routes.intelligence import router as intelligence_router
from app.api.routes.receivables import router as receivables_router
from app.api.routes.references import router as references_router
from app.api.routes.reports import router as reports_router


api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(references_router)
api_router.include_router(expenses_router)
api_router.include_router(exports_router)
api_router.include_router(receivables_router)
api_router.include_router(budgets_router)
api_router.include_router(reports_router)
api_router.include_router(imports_router)
api_router.include_router(intelligence_router)
api_router.include_router(automations_router)


__all__ = ["api_router"]
