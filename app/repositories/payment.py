from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment


class PaymentRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    def add(
        self,
        payment: Payment,
    ) -> None:
        self.session.add(payment)

    async def get_by_provider_id(
        self,
        provider_payment_id: str,
    ) -> Payment | None:
        result = await self.session.execute(
            select(Payment).where(
                Payment.provider_payment_id
                == provider_payment_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> Payment | None:
        result = await self.session.execute(
            select(Payment).where(
                Payment.idempotency_key
                == idempotency_key
            )
        )
        return result.scalar_one_or_none()

    async def list_for_subscription(
        self,
        subscription_id: UUID,
    ) -> list[Payment]:
        result = await self.session.execute(
            select(Payment)
            .where(
                Payment.subscription_id
                == subscription_id
            )
            .order_by(
                Payment.created_at.desc()
            )
        )
        return list(result.scalars().all())
