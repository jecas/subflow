from fastapi import APIRouter

from app.api.dependencies import (
    CurrentCustomer,
    DbSession,
)
from app.schemas.customer import (
    CustomerResponse,
    CustomerUpdate,
)


router = APIRouter(
    prefix="/customers",
    tags=["customers"],
)


@router.get(
    "/me",
    response_model=CustomerResponse,
)
async def me(
    customer: CurrentCustomer,
) -> CustomerResponse:
    return customer


@router.patch(
    "/me",
    response_model=CustomerResponse,
)
async def update_me(
    data: CustomerUpdate,
    customer: CurrentCustomer,
    session: DbSession,
) -> CustomerResponse:
    for field, value in data.model_dump(
        exclude_unset=True
    ).items():
        setattr(customer, field, value)

    await session.commit()
    await session.refresh(customer)

    return customer
