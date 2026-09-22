from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.plan import BillingPeriod


class PlanCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    price: Decimal = Field(gt=0)
    currency: str = Field(
        default="EUR",
        min_length=3,
        max_length=3,
    )
    billing_period: BillingPeriod

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class PlanUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    is_active: bool | None = None


class PlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    price: Decimal
    currency: str
    billing_period: BillingPeriod
    is_active: bool
    created_at: datetime
