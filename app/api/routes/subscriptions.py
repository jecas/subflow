from uuid import UUID

from fastapi import APIRouter, status

from app.api.dependencies import CurrentCustomer, DbSession
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse
from app.services.subscription import SubscriptionService

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
)


@router.post(
    "",
    response_model=SubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_subscription(
    data: SubscriptionCreate,
    customer: CurrentCustomer,
    session: DbSession,
) -> SubscriptionResponse:
    return await SubscriptionService(
        session
    ).create(
        customer.id,
        data.plan_id,
    )


@router.get(
    "/me",
    response_model=list[SubscriptionResponse],
)
async def my_subscriptions(
    customer: CurrentCustomer,
    session: DbSession,
) -> list[SubscriptionResponse]:
    return await SubscriptionService(
        session
    ).list_for_customer(customer.id)


@router.post(
    "/{subscription_id}/cancel",
    response_model=SubscriptionResponse,
)
async def cancel_subscription(
    subscription_id: UUID,
    customer: CurrentCustomer,
    session: DbSession,
) -> SubscriptionResponse:
    return await SubscriptionService(
        session
    ).cancel(
        customer.id,
        subscription_id,
    )
