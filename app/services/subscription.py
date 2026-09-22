import calendar
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.plan import BillingPeriod
from app.models.subscription import Subscription, SubscriptionStatus
from app.repositories.plan import PlanRepository
from app.repositories.subscription import SubscriptionRepository


def _add_months(value: datetime, months: int) -> datetime:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


def _next_period(value: datetime, billing_period: BillingPeriod) -> datetime:
    months = 1 if billing_period == BillingPeriod.MONTHLY else 12
    return _add_months(value, months)


class SubscriptionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.subscriptions = SubscriptionRepository(session)
        self.plans = PlanRepository(session)

    async def create(self, customer_id: UUID, plan_id: UUID) -> Subscription:
        plan = await self.plans.get(plan_id)
        if plan is None or not plan.is_active:
            raise NotFoundError("Active plan not found.")

        active = await self.subscriptions.get_active_for_customer(customer_id)
        if active:
            raise ConflictError("Customer already has an active subscription.")

        now = datetime.now(UTC)
        subscription = Subscription(
            customer_id=customer_id,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
            started_at=now,
            current_period_end=_next_period(now, plan.billing_period),
        )
        self.subscriptions.add(subscription)
        await self.session.commit()
        await self.session.refresh(subscription)
        return subscription

    async def list_for_customer(self, customer_id: UUID) -> list[Subscription]:
        return await self.subscriptions.list_for_customer(customer_id)

    async def cancel(self, customer_id: UUID, subscription_id: UUID) -> Subscription:
        subscription = await self._owned_active(customer_id, subscription_id)
        subscription.cancel_at_period_end = True
        await self.session.commit()
        await self.session.refresh(subscription)
        return subscription

    async def change_plan(
        self,
        customer_id: UUID,
        subscription_id: UUID,
        plan_id: UUID,
    ) -> Subscription:
        subscription = await self._owned_active(customer_id, subscription_id)
        plan = await self.plans.get(plan_id)
        if plan is None or not plan.is_active:
            raise NotFoundError("Active plan not found.")
        subscription.plan_id = plan.id
        await self.session.commit()
        await self.session.refresh(subscription)
        return subscription

    async def renew(self, subscription_id: UUID) -> Subscription:
        subscription = await self.subscriptions.get(subscription_id)
        if subscription is None:
            raise NotFoundError("Subscription not found.")
        if subscription.status != SubscriptionStatus.ACTIVE:
            raise ConflictError("Only active subscriptions can be renewed.")

        if subscription.cancel_at_period_end:
            subscription.status = SubscriptionStatus.CANCELED
            await self.session.commit()
            await self.session.refresh(subscription)
            return subscription

        plan = await self.plans.get(subscription.plan_id)
        if plan is None:
            raise NotFoundError("Plan not found.")

        subscription.current_period_end = _next_period(
            subscription.current_period_end,
            plan.billing_period,
        )
        await self.session.commit()
        await self.session.refresh(subscription)
        return subscription

    async def expire(self, subscription_id: UUID) -> Subscription:
        subscription = await self.subscriptions.get(subscription_id)
        if subscription is None:
            raise NotFoundError("Subscription not found.")
        subscription.status = SubscriptionStatus.EXPIRED
        await self.session.commit()
        await self.session.refresh(subscription)
        return subscription

    async def _owned_active(
        self,
        customer_id: UUID,
        subscription_id: UUID,
    ) -> Subscription:
        subscription = await self.subscriptions.get(subscription_id)
        if subscription is None or subscription.customer_id != customer_id:
            raise NotFoundError("Subscription not found.")
        if subscription.status != SubscriptionStatus.ACTIVE:
            raise ConflictError("Only active subscriptions can be modified.")
        return subscription
