import pytest

from app.core.exceptions import (
    ConflictError,
    NotFoundError,
)
from app.db.session import AsyncSessionFactory
from app.models.customer import Customer
from app.models.payment import PaymentStatus
from app.models.plan import BillingPeriod, Plan
from app.models.subscription import (
    SubscriptionStatus,
)
from app.services.payment import PaymentService
from app.services.subscription import (
    SubscriptionService,
)


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
            customer_id=customer.id,
            subscription_id=subscription.id,
            idempotency_key="payment-flow-1",
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

        assert (
            payment.idempotency_key
            == "payment-flow-1"
        )

        assert payment.provider_payment_id.startswith(
            "mock_payment-flow-1_"
        )


@pytest.mark.asyncio
async def test_same_idempotency_key_returns_same_payment() -> None:
    async with AsyncSessionFactory() as session:
        customer = Customer(
            email="idempotency@example.com",
            password_hash="not-used",
            first_name="Idempotency",
            last_name="Test",
        )

        plan = Plan(
            name="Idempotency Plan",
            price="39.99",
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

        service = PaymentService(session)

        first = await service.charge_subscription(
            customer_id=customer.id,
            subscription_id=subscription.id,
            idempotency_key="same-payment-key",
        )

        second = await service.charge_subscription(
            customer_id=customer.id,
            subscription_id=subscription.id,
            idempotency_key="same-payment-key",
        )

        assert first.id == second.id

        assert (
            first.provider_payment_id
            == second.provider_payment_id
        )


@pytest.mark.asyncio
async def test_different_idempotency_keys_create_different_payments() -> None:
    async with AsyncSessionFactory() as session:
        customer = Customer(
            email="different-keys@example.com",
            password_hash="not-used",
            first_name="Different",
            last_name="Keys",
        )

        plan = Plan(
            name="Different Keys Plan",
            price="49.99",
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

        service = PaymentService(session)

        first = await service.charge_subscription(
            customer_id=customer.id,
            subscription_id=subscription.id,
            idempotency_key="payment-key-1",
        )

        second = await service.charge_subscription(
            customer_id=customer.id,
            subscription_id=subscription.id,
            idempotency_key="payment-key-2",
        )

        assert first.id != second.id

        assert (
            first.provider_payment_id
            != second.provider_payment_id
        )


@pytest.mark.asyncio
async def test_customer_cannot_charge_another_customers_subscription() -> None:
    async with AsyncSessionFactory() as session:
        owner = Customer(
            email="owner@example.com",
            password_hash="not-used",
            first_name="Subscription",
            last_name="Owner",
        )

        other_customer = Customer(
            email="other@example.com",
            password_hash="not-used",
            first_name="Other",
            last_name="Customer",
        )

        plan = Plan(
            name="Ownership Plan",
            price="20.00",
            currency="EUR",
            billing_period=BillingPeriod.MONTHLY,
        )

        session.add_all(
            [
                owner,
                other_customer,
                plan,
            ]
        )

        await session.commit()

        await session.refresh(owner)
        await session.refresh(other_customer)
        await session.refresh(plan)

        subscription = await SubscriptionService(
            session
        ).create(
            owner.id,
            plan.id,
        )

        with pytest.raises(
            NotFoundError,
            match="Subscription not found",
        ):
            await PaymentService(
                session
            ).charge_subscription(
                customer_id=other_customer.id,
                subscription_id=subscription.id,
                idempotency_key="unauthorized-payment",
            )


@pytest.mark.asyncio
async def test_expired_subscription_cannot_be_charged() -> None:
    async with AsyncSessionFactory() as session:
        customer = Customer(
            email="expired-payment@example.com",
            password_hash="not-used",
            first_name="Expired",
            last_name="Payment",
        )

        plan = Plan(
            name="Expired Payment Plan",
            price="25.00",
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

        subscription.status = (
            SubscriptionStatus.EXPIRED
        )

        await session.commit()

        with pytest.raises(
            ConflictError,
            match=(
                "Only active subscriptions "
                "can be charged"
            ),
        ):
            await PaymentService(
                session
            ).charge_subscription(
                customer_id=customer.id,
                subscription_id=subscription.id,
                idempotency_key="expired-payment",
            )
