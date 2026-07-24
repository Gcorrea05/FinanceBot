from fastapi import (
    APIRouter,
    Depends,
    Query,
    Response,
    status,
)

from app.api.dependencies import get_container
from app.api.schemas.expense import (
    ExpenseCreateRequest,
    ExpenseListResponse,
    ExpenseResponse,
    ExpenseUpdateRequest,
)
from app.api.serializers import serialize_expense
from app.container import Container


router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
)


@router.post(
    "",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(
    payload: ExpenseCreateRequest,
    container: Container = Depends(get_container),
) -> ExpenseResponse:
    created = container.expense_service.create_expense(
        payload.to_domain()
    )

    detailed = container.expense_management_service.get(created.id)
    return serialize_expense(detailed)


@router.get(
    "",
    response_model=ExpenseListResponse,
)
def list_expenses(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    month: int | None = Query(default=None, ge=1, le=12),
    year: int | None = Query(default=None, ge=1),
    container: Container = Depends(get_container),
) -> ExpenseListResponse:
    page = container.expense_management_service.list(
        limit=limit,
        offset=offset,
        month=month,
        year=year,
    )

    return ExpenseListResponse(
        items=[
            serialize_expense(expense)
            for expense in page.items
        ],
        total=page.total,
        limit=page.limit,
        offset=page.offset,
    )


@router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
)
def get_expense(
    expense_id: int,
    container: Container = Depends(get_container),
) -> ExpenseResponse:
    expense = container.expense_management_service.get(expense_id)
    return serialize_expense(expense)


@router.put(
    "/{expense_id}",
    response_model=ExpenseResponse,
)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdateRequest,
    container: Container = Depends(get_container),
) -> ExpenseResponse:
    updated = container.expense_editor_service.update(
        expense_id,
        payload.to_domain(),
    )
    return serialize_expense(updated)


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_expense(
    expense_id: int,
    container: Container = Depends(get_container),
) -> Response:
    container.expense_management_service.delete(expense_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
