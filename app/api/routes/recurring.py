from fastapi import APIRouter, Depends, HTTPException, Path

from app.api.dependencies import get_container
from app.api.schemas.recurring import (
    RecurringExpenseResponse,
    RecurringExpenseUpdateRequest,
)
from app.container import Container

router = APIRouter(prefix="/recurring-expenses", tags=["recurring-expenses"])


def _serialize(item) -> RecurringExpenseResponse:
    return RecurringExpenseResponse(
        id=item.id,
        description=item.description,
        amount=item.amount,
        category=item.category.name,
        payment_method=item.payment_method.name,
        due_day=item.due_day,
        start_date=item.start_date,
        end_date=item.end_date,
        active=item.active,
        auto_post=item.auto_post,
    )


@router.get("", response_model=list[RecurringExpenseResponse])
def list_recurring(
    container: Container = Depends(get_container),
) -> list[RecurringExpenseResponse]:
    return [_serialize(item) for item in container.recurring_expense_repository.list_all()]


@router.put("/{recurring_id}", response_model=RecurringExpenseResponse)
def update_recurring(
    payload: RecurringExpenseUpdateRequest,
    recurring_id: int = Path(ge=1),
    container: Container = Depends(get_container),
) -> RecurringExpenseResponse:
    item = next(
        (
            row
            for row in container.recurring_expense_repository.list_all()
            if row.id == recurring_id
        ),
        None,
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Gasto recorrente nao encontrado.")
    updated = container.recurring_expense_service.update_recurring(
        item,
        amount=payload.amount,
        due_day=payload.due_day,
        active=payload.active,
        auto_post=payload.auto_post,
    )
    return _serialize(updated)
