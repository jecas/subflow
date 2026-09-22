from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.payment import Payment, PaymentStatus
from app.providers.payment import MockPaymentProvider, PaymentProvider
from app.repositories.payment import PaymentRepository
from app.repositories.plan import PlanRepository
from app.repositories.subscription import SubscriptionRepository


class PaymentService:
    def __init__(
        self,
        session: AsyncSession,
        provider: PaymentProvider | None = None,
    ):
        self.session = session
        self.provider = provider or MockPaymentProvider()
        self.payments = PaymentRepository(session)
        self.subscriptions = SubscriptionRepository(session)
        self.plans = PlanRepository(session)

    async def charge_subscription(
        self,
        subscription_id: UUID,
        idempotency_key: str,
    ) -> Payment:
        subscription = await self.subscriptions.get(subscription_id)
        if subscription is None:
            raise NotFoundError("Subscription not found.")

        plan = await self.plans.get(subscription.plan_id)
        if plan is None:
            raise NotFoundError("Plan not found.")

        result = await self.provider.charge(
            amount=plan.price,
            currency=plan.currency,
            idempotency_key=idempotency_key,
        )
        payment = Payment(
            subscription_id=subscription.id,
            amount=plan.price,
            currency=plan.currency,
            provider_payment_id=result.provider_payment_id,
            status=PaymentStatus.SUCCEEDED if result.succeeded else PaymentStatus.FAILED,
            paid_at=datetime.now(UTC) if result.succeeded else None,
        )
        self.payments.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment
