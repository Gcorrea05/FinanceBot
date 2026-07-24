import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.domain.exceptions import DomainError
from app.imports.parser import ImportFileError
from app.services.expense_editor_service import ExpenseMutationConflictError
from app.services.expense_management_service import ExpenseNotFoundError
from app.services.import_service import ImportBatchNotFoundError, ImportConflictError
from app.services.lookup_service import LookupNotFoundError
from app.services.receivable_service import ReceivableNotFoundError


logger = logging.getLogger(__name__)


def register_exception_handlers(application: FastAPI) -> None:
    def response(status_code: int, detail: str, code: str) -> JSONResponse:
        return JSONResponse(status_code=status_code, content={"detail": detail, "code": code})

    @application.exception_handler(ExpenseNotFoundError)
    async def expense_not_found_handler(request: Request, error: ExpenseNotFoundError) -> JSONResponse:
        del request
        return response(404, str(error), "expense_not_found")

    @application.exception_handler(ExpenseMutationConflictError)
    async def expense_conflict_handler(request: Request, error: ExpenseMutationConflictError) -> JSONResponse:
        del request
        return response(409, str(error), "expense_mutation_conflict")

    @application.exception_handler(ReceivableNotFoundError)
    async def receivable_not_found_handler(request: Request, error: ReceivableNotFoundError) -> JSONResponse:
        del request
        return response(404, str(error), "receivable_not_found")

    @application.exception_handler(ImportBatchNotFoundError)
    async def import_not_found_handler(request: Request, error: ImportBatchNotFoundError) -> JSONResponse:
        del request
        return response(404, str(error), "import_not_found")

    @application.exception_handler(ImportConflictError)
    async def import_conflict_handler(request: Request, error: ImportConflictError) -> JSONResponse:
        del request
        return response(409, str(error), "import_conflict")

    @application.exception_handler(ImportFileError)
    async def import_file_handler(request: Request, error: ImportFileError) -> JSONResponse:
        del request
        return response(422, str(error), "invalid_import_file")

    @application.exception_handler(LookupNotFoundError)
    async def lookup_error_handler(request: Request, error: LookupNotFoundError) -> JSONResponse:
        del request
        return response(422, str(error), "invalid_reference")

    @application.exception_handler(DomainError)
    async def domain_error_handler(request: Request, error: DomainError) -> JSONResponse:
        del request
        content = {"detail": str(error), "code": "domain_validation_error"}
        field = getattr(error, "field", None)
        if field is not None:
            content["field"] = field
        return JSONResponse(status_code=422, content=content)

    @application.exception_handler(SQLAlchemyError)
    async def database_error_handler(request: Request, error: SQLAlchemyError) -> JSONResponse:
        logger.exception("Database error while handling %s", request.url.path, exc_info=error)
        return response(500, "The database operation failed.", "database_error")
