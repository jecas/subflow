from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import update

from app.db.session import AsyncSessionFactory
from app.main import app
from app.models.customer import Customer, CustomerRole


@pytest.mark.asyncio
async def test_complete_subscription_flow() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "admin@example.com",
                "password": "StrongPassword123!",
                "first_name": "SubFlow",
                "last_name": "Admin",
            },
        )

        assert register_response.status_code == 201, register_response.text

        registered_customer = register_response.json()

        assert registered_customer["email"] == "admin@example.com"

        customer_id = UUID(
            registered_customer["id"]
        )

        async with AsyncSessionFactory() as session:
            await session.execute(
                update(Customer)
                .where(Customer.id == customer_id)
                .values(role=CustomerRole.ADMIN)
            )
            await session.commit()

        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin@example.com",
                "password": "StrongPassword123!",
            },
        )

        assert login_response.status_code == 200, login_response.text

        login_data = login_response.json()

        assert login_data["access_token"]
        assert login_data["token_type"] == "bearer"

        headers = {
            "Authorization": (
                f"Bearer {login_data['access_token']}"
            )
        }

        create_plan_response = await client.post(
            "/api/v1/admin/plans",
            headers=headers,
            json={
                "name": "Pro",
                "description": "Professional subscription plan",
                "price": "29.99",
                "currency": "EUR",
                "billing_period": "monthly",
            },
        )

        assert create_plan_response.status_code == 201

        plan = create_plan_response.json()

        assert plan["name"] == "Pro"
        assert plan["price"] == "29.99"
        assert plan["billing_period"] == "monthly"
        assert plan["is_active"] is True

        plan_id = plan["id"]

        plans_response = await client.get(
            "/api/v1/plans"
        )

        assert plans_response.status_code == 200

        plans = plans_response.json()

        assert len(plans) == 1
        assert plans[0]["id"] == plan_id

        subscription_response = await client.post(
            "/api/v1/subscriptions",
            headers=headers,
            json={
                "plan_id": plan_id,
            },
        )

        assert subscription_response.status_code == 201

        subscription = subscription_response.json()

        assert subscription["plan_id"] == plan_id
        assert subscription["customer_id"] == str(
            customer_id
        )
        assert subscription["status"] == "active"
        assert subscription["cancel_at_period_end"] is False

        subscription_id = subscription["id"]

        my_subscriptions_response = await client.get(
            "/api/v1/subscriptions/me",
            headers=headers,
        )

        assert my_subscriptions_response.status_code == 200

        subscriptions = my_subscriptions_response.json()

        assert len(subscriptions) == 1
        assert subscriptions[0]["id"] == subscription_id

        cancel_response = await client.post(
            (
                "/api/v1/subscriptions/"
                f"{subscription_id}/cancel"
            ),
            headers=headers,
        )

        assert cancel_response.status_code == 200

        canceled_subscription = cancel_response.json()

        assert (
            canceled_subscription["cancel_at_period_end"]
            is True
        )
        assert canceled_subscription["status"] == "active"
