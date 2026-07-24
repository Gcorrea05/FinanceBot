from fastapi import APIRouter

from app.api.routes.expenses import (
    router as expenses_router,
)
from app.api.routes.health import (
    router as health_router,
)
from app.api.routes.receivables import (
    router as receivables_router,
)
from app.api.routes.references import (
    router as references_router,
)


api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(
    references_router
)
api_router.include_router(expenses_router)
api_router.include_router(
    receivables_router
)


__all__ = ["api_router"]
