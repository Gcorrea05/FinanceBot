from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.errors import register_exception_handlers
from app.api.routes import api_router
from app.core.logging import configure_logging
from app.core.request_context import RequestContextMiddleware
from app.core.settings import settings


def create_app() -> FastAPI:
    configure_logging("api")
    docs_enabled = settings.security.expose_api_docs

    application = FastAPI(
        title=settings.api.title,
        version=settings.api.version,
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
    )
    application.add_middleware(RequestContextMiddleware)
    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=list(
                dict.fromkeys(
                    [
                        *settings.security.trusted_hosts,
                        "testserver",
                    ]
                )
            ),
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router, prefix="/api/v1")
    register_exception_handlers(application)
    return application
