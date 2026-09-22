from uuid import UUID

from fastapi import APIRouter, Header, status

from app.api.dependencies import CurrentCustomer, DbSession
from app.schemas.payment import PaymentResponse
from app.schemas.subscription import (
    SubscriptionChangePlan,
    SubscriptionCreate,
    SubscriptionResponse,
)
from app.services.payment import PaymentService
from app.services.subscription import SubscriptionService

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    data: SubscriptionCreate,
    customer: CurrentCustomer,
    session: DbSession,
) -> SubscriptionResponse:
    return await SubscriptionService(session).create(customer.id, data.plan_id)


@router.get("/me", response_model=list[SubscriptionResponse])
async def my_subscriptions(
    customer: CurrentCustomer,
    session: DbSession,
) -> list[SubscriptionResponse]:
    return await SubscriptionService(session).list_for_customer(customer.id)


@router.post("/{subscription_id}/cancel", response_model=SubscriptionResponse)
async def cancel_subscription(
    subscription_id: UUID,
    customer: CurrentCustomer,
    session: DbSession,
) -> SubscriptionResponse:
    return await SubscriptionService(session).cancel(customer.id, subscription_id)


@router.post("/{subscription_id}/change-plan", response_model=SubscriptionResponse)
async def change_plan(
    subscription_id: UUID,
    data: SubscriptionChangePlan,
    customer: CurrentCustomer,
    session: DbSession,
) -> SubscriptionResponse:
    return await SubscriptionService(session).change_plan(
        customer.id,
        subscription_id,
        data.plan_id,
    )


@router.post("/{subscription_id}/payments", response_model=PaymentResponse)
async def create_payment(
    subscription_id: UUID,
    customer: CurrentCustomer,
    session: DbSession,
    idempotency_key: str = Header(alias="Idempotency-Key"),
) -> PaymentResponse:
    subscription = await SubscriptionService(session)._owned_active(
        customer.id,
        subscription_id,
    )
    return await PaymentService(session).charge_subscription(
        subscription.id,
        idempotency_key,
    )
