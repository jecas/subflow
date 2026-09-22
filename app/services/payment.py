from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.payment import Payment, PaymentStatus
from app.models.subscription import SubscriptionStatus
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
        customer_id: UUID,
        subscription_id: UUID,
        idempotency_key: str,
    ) -> Payment:
        existing_payment = (
            await self.payments.get_by_idempotency_key(
                idempotency_key
            )
        )

        if existing_payment is not None:
            if (
                existing_payment.subscription_id
                != subscription_id
            ):
                raise ConflictError(
                    "Idempotency key is already in use."
                )

            return existing_payment

        subscription = await self.subscriptions.get(
            subscription_id
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
                "Only active subscriptions can be charged."
            )

        plan = await self.plans.get(
            subscription.plan_id
        )

        if plan is None:
            raise NotFoundError(
                "Plan not found."
            )

        result = await self.provider.charge(
            amount=plan.price,
            currency=plan.currency,
            idempotency_key=idempotency_key,
        )

        payment = Payment(
            subscription_id=subscription.id,
            amount=plan.price,
            currency=plan.currency,
            provider_payment_id=(
                result.provider_payment_id
            ),
            idempotency_key=idempotency_key,
            status=(
                PaymentStatus.SUCCEEDED
                if result.succeeded
                else PaymentStatus.FAILED
            ),
            paid_at=(
                datetime.now(UTC)
                if result.succeeded
                else None
            ),
        )

        self.payments.add(payment)

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()

            existing_payment = (
                await self.payments.get_by_idempotency_key(
                    idempotency_key
                )
            )

            if (
                existing_payment is not None
                and existing_payment.subscription_id
                == subscription_id
            ):
                return existing_payment

            raise

        await self.session.refresh(payment)

        return payment
