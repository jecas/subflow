from uuid import UUID

from fastapi import APIRouter, status

from app.api.dependencies import AdminCustomer, DbSession
from app.repositories.customer import CustomerRepository
from app.repositories.subscription import SubscriptionRepository
from app.schemas.customer import CustomerResponse
from app.schemas.plan import PlanCreate, PlanResponse, PlanUpdate
from app.schemas.subscription import SubscriptionResponse
from app.services.plan import PlanService
from app.services.subscription import SubscriptionService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/plans", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    data: PlanCreate,
    session: DbSession,
    _: AdminCustomer,
) -> PlanResponse:
    return await PlanService(session).create(data)


@router.patch("/plans/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: UUID,
    data: PlanUpdate,
    session: DbSession,
    _: AdminCustomer,
) -> PlanResponse:
    return await PlanService(session).update(plan_id, data)


@router.get("/customers", response_model=list[CustomerResponse])
async def list_customers(
    session: DbSession,
    _: AdminCustomer,
) -> list[CustomerResponse]:
    return await CustomerRepository(session).list_all()


@router.get("/subscriptions", response_model=list[SubscriptionResponse])
async def list_subscriptions(
    session: DbSession,
    _: AdminCustomer,
) -> list[SubscriptionResponse]:
    return await SubscriptionRepository(session).list_all()


@router.post("/subscriptions/{subscription_id}/renew", response_model=SubscriptionResponse)
async def renew_subscription(
    subscription_id: UUID,
    session: DbSession,
    _: AdminCustomer,
) -> SubscriptionResponse:
    return await SubscriptionService(session).renew(subscription_id)


@router.post("/subscriptions/{subscription_id}/expire", response_model=SubscriptionResponse)
async def expire_subscription(
    subscription_id: UUID,
    session: DbSession,
    _: AdminCustomer,
) -> SubscriptionResponse:
    return await SubscriptionService(session).expire(subscription_id)
