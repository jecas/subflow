from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import (
    Subscription,
    SubscriptionStatus,
)


class SubscriptionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(
        self,
        subscription_id: UUID,
    ) -> Subscription | None:
        return await self.session.get(
            Subscription,
            subscription_id,
        )

    async def get_active_for_customer(
        self,
        customer_id: UUID,
    ) -> Subscription | None:
        result = await self.session.execute(
            select(Subscription).where(
                Subscription.customer_id == customer_id,
                Subscription.status
                == SubscriptionStatus.ACTIVE,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_customer(
        self,
        customer_id: UUID,
    ) -> list[Subscription]:
        result = await self.session.execute(
            select(Subscription)
            .where(
                Subscription.customer_id == customer_id
            )
            .order_by(
                Subscription.created_at.desc()
            )
        )
        return list(result.scalars().all())

    async def list_all(self) -> list[Subscription]:
        result = await self.session.execute(
            select(Subscription).order_by(
                Subscription.created_at.desc()
            )
        )
        return list(result.scalars().all())

    def add(
        self,
        subscription: Subscription,
    ) -> None:
        self.session.add(subscription)
