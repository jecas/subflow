import pytest

from app.db.session import AsyncSessionFactory
from app.models.customer import Customer
from app.models.payment import PaymentStatus
from app.models.plan import BillingPeriod, Plan
from app.services.payment import PaymentService
from app.services.subscription import SubscriptionService


@pytest.mark.asyncio
async def test_mock_payment_is_persisted() -> None:
    async with AsyncSessionFactory() as session:
        customer = Customer(
            email="payment@example.com",
            password_hash="not-used",
            first_name="Payment",
            last_name="Test",
        )

        plan = Plan(
            name="Payment Plan",
            price="29.99",
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
            subscription.id,
            "payment-flow-1",
        )

        assert (
            payment.subscription_id
            == subscription.id
        )

        assert (
            payment.status
            == PaymentStatus.SUCCEEDED
        )

        assert payment.amount == plan.price
        assert payment.currency == "EUR"
        assert payment.paid_at is not None

        assert payment.provider_payment_id.startswith(
            "mock_payment-flow-1_"
        )
