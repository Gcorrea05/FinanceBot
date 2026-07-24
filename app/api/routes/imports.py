import json

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from pydantic import ValidationError

from app.api.dependencies import get_container
from app.api.schemas.imports import (
    ImportBatchResponse,
    ImportColumnMappingRequest,
    ImportHistoryResponse,
    ImportInspectionResponse,
    ImportRowResponse,
)
from app.container import Container
from app.database.models import ImportBatch
from app.imports.parser import ImportColumnMapping, ImportFileError


MAX_FILE_SIZE = 5 * 1024 * 1024

router = APIRouter(prefix="/imports", tags=["imports"])


def serialize_batch(batch: ImportBatch, include_rows: bool = True) -> ImportBatchResponse:
    return ImportBatchResponse(
        id=batch.id,
        filename=batch.filename,
        source_type=batch.source_type,
        status=batch.status,
        default_category=batch.default_category,
        default_payment_method=batch.default_payment_method,
        total_rows=batch.total_rows,
        ready_rows=batch.ready_rows,
        duplicate_rows=batch.duplicate_rows,
        invalid_rows=batch.invalid_rows,
        imported_rows=batch.imported_rows,
        created_at=batch.created_at,
        completed_at=batch.completed_at,
        rows=[
            ImportRowResponse(
                id=row.id,
                row_number=row.row_number,
                purchase_date=row.purchase_date,
                purchase_place=row.purchase_place,
                purchase_value=row.purchase_value,
                external_id=row.external_id,
                status=row.status,
                error_message=row.error_message,
                expense_id=row.expense_id,
            )
            for row in batch.rows
        ] if include_rows else [],
    )


async def _read_upload(file: UploadFile) -> tuple[str, bytes]:
    filename = file.filename or "importacao"
    content = await file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise ImportFileError("O arquivo excede o limite de 5 MB.")
    return filename, content


def _parse_mapping(mapping_json: str | None) -> ImportColumnMapping | None:
    if not mapping_json:
        return None
    try:
        payload = ImportColumnMappingRequest.model_validate(json.loads(mapping_json))
    except (json.JSONDecodeError, ValidationError) as error:
        raise ImportFileError("O mapeamento de colunas e invalido.") from error

    return ImportColumnMapping(
        sheet_name=payload.sheet_name,
        data_start_row=payload.data_start_row,
        date_column=payload.date_column,
        description_columns=tuple(payload.description_columns),
        amount_column=payload.amount_column,
        external_id_column=payload.external_id_column,
        date_format=payload.date_format,
        decimal_separator=payload.decimal_separator,
        amount_mode=payload.amount_mode,
    )


@router.post("/inspect", response_model=ImportInspectionResponse)
async def inspect_import(
    file: UploadFile = File(...),
    sheet_name: str | None = Form(default=None),
    container: Container = Depends(get_container),
) -> ImportInspectionResponse:
    filename, content = await _read_upload(file)
    inspection = container.import_service.inspect(
        filename=filename,
        content=content,
        sheet_name=sheet_name,
    )
    return ImportInspectionResponse(
        source_type=inspection.source_type,
        sheets=list(inspection.sheets),
        selected_sheet=inspection.selected_sheet,
        total_rows=inspection.total_rows,
        max_columns=inspection.max_columns,
        rows=[list(row) for row in inspection.rows],
        mapping_required=inspection.mapping_required,
    )


@router.post("/preview", response_model=ImportBatchResponse, status_code=status.HTTP_201_CREATED)
async def preview_import(
    file: UploadFile = File(...),
    default_category: str = Form(..., min_length=2, max_length=100),
    default_payment_method: str = Form(..., min_length=2, max_length=100),
    mapping_json: str | None = Form(default=None),
    container: Container = Depends(get_container),
) -> ImportBatchResponse:
    filename, content = await _read_upload(file)
    batch = container.import_service.preview(
        filename=filename,
        content=content,
        default_category=default_category,
        default_payment_method=default_payment_method,
        mapping=_parse_mapping(mapping_json),
    )
    return serialize_batch(batch)


@router.post("/{batch_id}/confirm", response_model=ImportBatchResponse)
def confirm_import(
    batch_id: int,
    container: Container = Depends(get_container),
) -> ImportBatchResponse:
    return serialize_batch(container.import_service.confirm(batch_id))


@router.get("", response_model=ImportHistoryResponse)
def list_imports(
    limit: int = Query(default=20, ge=1, le=100),
    container: Container = Depends(get_container),
) -> ImportHistoryResponse:
    return ImportHistoryResponse(
        items=[
            serialize_batch(batch, include_rows=False)
            for batch in container.import_service.list_history(limit)
        ]
    )


@router.get("/{batch_id}", response_model=ImportBatchResponse)
def get_import(
    batch_id: int,
    container: Container = Depends(get_container),
) -> ImportBatchResponse:
    return serialize_batch(container.import_service.get(batch_id))
