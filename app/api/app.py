from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware,
)

from app.api.errors import (
    register_exception_handlers,
)
from app.api.routes import api_router
from app.api.settings import api_settings


def create_app() -> FastAPI:
    application = FastAPI(
        title=api_settings.title,
        version=api_settings.version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=(
            api_settings.cors_origins
        ),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(
        api_router,
        prefix="/api/v1",
    )

    register_exception_handlers(
        application
    )

    return application
