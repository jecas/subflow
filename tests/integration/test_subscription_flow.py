from datetime import UTC, datetime

import pytest

from app.db.session import AsyncSessionFactory
from app.models.customer import Customer, CustomerRole
from app.models.plan import BillingPeriod, Plan
from app.models.subscription import (
    Subscription,
    SubscriptionStatus,
)
from app.services.subscription import SubscriptionService


@pytest.mark.asyncio
async def test_change_plan_renew_and_expire() -> None:
    async with AsyncSessionFactory() as session:
        customer = Customer(
            email="lifecycle@example.com",
            password_hash="not-used",
            first_name="Life",
            last_name="Cycle",
            role=CustomerRole.CUSTOMER,
        )

        monthly = Plan(
            name="Monthly",
            price="10.00",
            currency="EUR",
            billing_period=BillingPeriod.MONTHLY,
        )

        yearly = Plan(
            name="Yearly",
            price="100.00",
            currency="EUR",
            billing_period=BillingPeriod.YEARLY,
        )

        session.add_all(
            [
                customer,
                monthly,
                yearly,
            ]
        )

        await session.commit()

        await session.refresh(customer)
        await session.refresh(monthly)
        await session.refresh(yearly)

        service = SubscriptionService(session)

        subscription = await service.create(
            customer.id,
            monthly.id,
        )

        changed = await service.change_plan(
            customer.id,
            subscription.id,
            yearly.id,
        )

        assert changed.plan_id == yearly.id

        old_period_end = changed.current_period_end

        renewed = await service.renew(
            changed.id
        )

        assert (
            renewed.status
            == SubscriptionStatus.ACTIVE
        )

        assert (
            renewed.current_period_end
            > old_period_end
        )

        expired = await service.expire(
            renewed.id
        )

        assert (
            expired.status
            == SubscriptionStatus.EXPIRED
        )


@pytest.mark.asyncio
async def test_cancel_at_period_end_becomes_canceled_on_renewal() -> None:
    async with AsyncSessionFactory() as session:
        customer = Customer(
            email="cancel@example.com",
            password_hash="not-used",
            first_name="Cancel",
            last_name="Test",
        )

        plan = Plan(
            name="Cancel Plan",
            price="15.00",
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

        service = SubscriptionService(session)

        subscription = await service.create(
            customer.id,
            plan.id,
        )

        canceled_later = await service.cancel(
            customer.id,
            subscription.id,
        )

        assert (
            canceled_later.cancel_at_period_end
            is True
        )

        assert (
            canceled_later.status
            == SubscriptionStatus.ACTIVE
        )

        processed = await service.renew(
            subscription.id
        )

        assert (
            processed.status
            == SubscriptionStatus.CANCELED
        )


@pytest.mark.asyncio
async def test_january_31_monthly_subscription_uses_calendar_month() -> None:
    async with AsyncSessionFactory() as session:
        customer = Customer(
            email="calendar@example.com",
            password_hash="not-used",
            first_name="Calendar",
            last_name="Test",
        )

        plan = Plan(
            name="Calendar Plan",
            price="12.00",
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

        subscription = Subscription(
            customer_id=customer.id,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
            started_at=datetime(
                2026,
                1,
                31,
                tzinfo=UTC,
            ),
            current_period_end=datetime(
                2026,
                1,
                31,
                tzinfo=UTC,
            ),
        )

        session.add(subscription)

        await session.commit()
        await session.refresh(subscription)

        renewed = await SubscriptionService(
            session
        ).renew(subscription.id)

        assert (
            renewed.current_period_end
            == datetime(
                2026,
                2,
                28,
                tzinfo=UTC,
            )
        )
