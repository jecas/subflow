import pytest

from app.db.session import AsyncSessionFactory
from app.models.customer import Customer
from app.models.payment import PaymentStatus
from app.models.plan import BillingPeriod, Plan
from app.schemas.webhook import PaymentWebhook
from app.services.payment import PaymentService
from app.services.subscription import (
    SubscriptionService,
)
from app.services.webhook import WebhookService


@pytest.mark.asyncio
async def test_duplicate_webhook_is_not_processed_twice() -> None:
    async with AsyncSessionFactory() as session:
        customer = Customer(
            email="webhook@example.com",
            password_hash="not-used",
            first_name="Webhook",
            last_name="Test",
        )

        plan = Plan(
            name="Webhook Plan",
            price="19.99",
            currency="EUR",
            billing_period=BillingPeriod.MONTHLY,
        )

        session.add_all(
            [
                customer,
                plan,
            ]
        )

        await session.commit()

        await session.refresh(customer)
        await session.refresh(plan)

        subscription = await SubscriptionService(
            session
        ).create(
            customer.id,
            plan.id,
        )

        payment = await PaymentService(
            session
        ).charge_subscription(
            customer_id=customer.id,
            subscription_id=subscription.id,
            idempotency_key="webhook-payment",
        )

        event = PaymentWebhook(
            event_id="evt_123",
            event_type="payment.failed",
            payment_id=payment.provider_payment_id,
        )

        service = WebhookService(session)

        first = await service.process_payment_event(
            event
        )

        second = await service.process_payment_event(
            event
        )

        assert first.processed is True
        assert first.duplicate is False

        assert second.processed is True
        assert second.duplicate is True

        await session.refresh(payment)

        assert (
            payment.status
            == PaymentStatus.FAILED
        )
