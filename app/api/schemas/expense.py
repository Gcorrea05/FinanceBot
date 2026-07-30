
from datetime import date, datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)

from app.schemas.expense.create import ExpenseCreate
from app.schemas.expense.shared_person import SharedPersonCreate


class SharedPersonRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=120,
    )
    amount: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )


class ExpenseCreateRequest(BaseModel):
    purchase_date: datetime
    purchase_place: str = Field(
        min_length=2,
        max_length=255,
    )
    purchase_value: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    category: str = Field(
        min_length=2,
        max_length=100,
    )
    payment_method: str = Field(
        min_length=2,
        max_length=100,
    )
    is_installment: bool = False
    installments: int = Field(
        default=1,
        ge=1,
        le=120,
    )
    first_installment_due_date: date | None = None
    is_shared: bool = False
    shared_people: list[SharedPersonRequest] = Field(
        default_factory=list,
    )
    owner_amount: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    notes: str | None = Field(
        default=None,
        max_length=500,
    )

    @model_validator(mode="after")
    def validate_business_shape(self):
        if self.is_installment:
            if self.installments < 1:
                raise ValueError(
                    "An installment expense must have at least 1 installment."
                )

            if self.first_installment_due_date is None:
                raise ValueError(
                    "first_installment_due_date is required."
                )
        else:
            if self.installments != 1:
                raise ValueError(
                    "A non-installment expense must have 1 installment."
                )

            if self.first_installment_due_date is not None:
                raise ValueError(
                    "first_installment_due_date must be empty."
                )

        if self.is_shared:
            if not self.shared_people:
                raise ValueError(
                    "A shared expense must have at least one participant."
                )
        elif self.shared_people or self.owner_amount is not None:
            raise ValueError(
                "shared_people and owner_amount must be empty when is_shared is false."
            )

        return self

    def to_domain(self) -> ExpenseCreate:
        return ExpenseCreate(
            purchase_date=self.purchase_date,
            purchase_place=self.purchase_place,
            purchase_value=self.purchase_value,
            category=self.category,
            payment_method=self.payment_method,
            is_installment=self.is_installment,
            installments=self.installments,
            first_installment_due_date=self.first_installment_due_date,
            is_shared=self.is_shared,
            owner_amount=self.owner_amount,
            shared_people=tuple(
                SharedPersonCreate(
                    name=person.name,
                    amount=person.amount,
                )
                for person in self.shared_people
            ),
            notes=self.notes,
        )


class ExpenseUpdateRequest(ExpenseCreateRequest):
    """Complete replacement payload used by the web editor."""


class InstallmentResponse(BaseModel):
    id: int
    installment_number: int
    total_installments: int
    due_date: date
    amount: Decimal
    is_paid: bool
    paid_at: datetime | None


class SharedPersonResponse(BaseModel):
    receivable_id: int
    person_id: int
    person_name: str
    amount: Decimal
    is_settled: bool
    settled_at: datetime | None


class ExpenseResponse(BaseModel):
    id: int
    purchase_date: datetime
    purchase_place: str
    purchase_value: Decimal
    category: str
    payment_method: str
    is_installment: bool
    is_shared: bool
    owner_amount: Decimal
    notes: str | None
    created_at: datetime
    updated_at: datetime
    installments: list[InstallmentResponse]
    shared_people: list[SharedPersonResponse]


class ExpenseListResponse(BaseModel):
    items: list[ExpenseResponse]
    total: int
    limit: int
    offset: int
