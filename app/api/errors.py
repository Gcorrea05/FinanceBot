import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.domain.exceptions import DomainError
from app.services.expense_editor_service import ExpenseMutationConflictError
from app.services.expense_management_service import ExpenseNotFoundError
from app.services.lookup_service import LookupNotFoundError
from app.services.receivable_service import ReceivableNotFoundError


logger = logging.getLogger(__name__)


def register_exception_handlers(application: FastAPI) -> None:
    @application.exception_handler(ExpenseNotFoundError)
    async def expense_not_found_handler(
        request: Request,
        error: ExpenseNotFoundError,
    ) -> JSONResponse:
        del request
        return JSONResponse(
            status_code=404,
            content={
                "detail": str(error),
                "code": "expense_not_found",
            },
        )

    @application.exception_handler(ExpenseMutationConflictError)
    async def expense_conflict_handler(
        request: Request,
        error: ExpenseMutationConflictError,
    ) -> JSONResponse:
        del request
        return JSONResponse(
            status_code=409,
            content={
                "detail": str(error),
                "code": "expense_mutation_conflict",
            },
        )

    @application.exception_handler(ReceivableNotFoundError)
    async def receivable_not_found_handler(
        request: Request,
        error: ReceivableNotFoundError,
    ) -> JSONResponse:
        del request
        return JSONResponse(
            status_code=404,
            content={
                "detail": str(error),
                "code": "receivable_not_found",
            },
        )

    @application.exception_handler(LookupNotFoundError)
    async def lookup_error_handler(
        request: Request,
        error: LookupNotFoundError,
    ) -> JSONResponse:
        del request
        return JSONResponse(
            status_code=422,
            content={
                "detail": str(error),
                "code": "invalid_reference",
            },
        )

    @application.exception_handler(DomainError)
    async def domain_error_handler(
        request: Request,
        error: DomainError,
    ) -> JSONResponse:
        del request
        field = getattr(error, "field", None)
        content = {
            "detail": str(error),
            "code": "domain_validation_error",
        }

        if field is not None:
            content["field"] = field

        return JSONResponse(
            status_code=422,
            content=content,
        )

    @application.exception_handler(SQLAlchemyError)
    async def database_error_handler(
        request: Request,
        error: SQLAlchemyError,
    ) -> JSONResponse:
        logger.exception(
            "Database error while handling %s",
            request.url.path,
            exc_info=error,
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "The database operation failed.",
                "code": "database_error",
            },
        )
