from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    NotFoundError,
)
from app.models.plan import BillingPeriod
from app.models.subscription import (
    Subscription,
    SubscriptionStatus,
)
from app.repositories.plan import PlanRepository
from app.repositories.subscription import (
    SubscriptionRepository,
)


class SubscriptionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.subscriptions = SubscriptionRepository(
            session
        )
        self.plans = PlanRepository(session)

    async def create(
        self,
        customer_id: UUID,
        plan_id: UUID,
    ) -> Subscription:
        plan = await self.plans.get(plan_id)

        if plan is None or not plan.is_active:
            raise NotFoundError(
                "Active plan not found."
            )

        active = (
            await self.subscriptions
            .get_active_for_customer(customer_id)
        )

        if active:
            raise ConflictError(
                "Customer already has an active subscription."
            )

        now = datetime.now(timezone.utc)

        if plan.billing_period == BillingPeriod.MONTHLY:
            period = timedelta(days=30)
        else:
            period = timedelta(days=365)

        subscription = Subscription(
            customer_id=customer_id,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
            started_at=now,
            current_period_end=now + period,
        )

        self.subscriptions.add(subscription)

        await self.session.commit()
        await self.session.refresh(subscription)

        return subscription

    async def list_for_customer(
        self,
        customer_id: UUID,
    ) -> list[Subscription]:
        return (
            await self.subscriptions
            .list_for_customer(customer_id)
        )

    async def cancel(
        self,
        customer_id: UUID,
        subscription_id: UUID,
    ) -> Subscription:
        subscription = (
            await self.subscriptions.get(
                subscription_id
            )
        )

        if (
            subscription is None
            or subscription.customer_id != customer_id
        ):
            raise NotFoundError(
                "Subscription not found."
            )

        if (
            subscription.status
            != SubscriptionStatus.ACTIVE
        ):
            raise ConflictError(
                "Only active subscriptions can be canceled."
            )

        subscription.cancel_at_period_end = True

        await self.session.commit()
        await self.session.refresh(subscription)

        return subscription
