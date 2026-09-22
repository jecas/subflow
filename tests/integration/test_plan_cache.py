import json

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import update

from app.core.redis import redis_client
from app.db.session import AsyncSessionFactory
from app.main import app
from app.models.customer import Customer, CustomerRole


@pytest.mark.asyncio
async def test_plans_are_cached_and_invalidated() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        email = "cache-admin@example.com"
        password = "StrongPassword123!"

        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": password,
                "first_name": "Cache",
                "last_name": "Admin",
            },
        )

        assert (
            register_response.status_code == 201
        ), register_response.text

        customer_id = register_response.json()["id"]

        async with AsyncSessionFactory() as session:
            await session.execute(
                update(Customer)
                .where(
                    Customer.id == customer_id
                )
                .values(
                    role=CustomerRole.ADMIN
                )
            )
            await session.commit()

        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": email,
                "password": password,
            },
        )

        assert (
            login_response.status_code == 200
        ), login_response.text

        token = login_response.json()[
            "access_token"
        ]

        headers = {
            "Authorization": f"Bearer {token}"
        }

        create_response = await client.post(
            "/api/v1/admin/plans",
            headers=headers,
            json={
                "name": "Pro",
                "description": "Pro subscription",
                "price": "29.99",
                "currency": "EUR",
                "billing_period": "monthly",
            },
        )

        assert (
            create_response.status_code == 201
        ), create_response.text

        assert (
            await redis_client.get(
                "plans:active"
            )
            is None
        )

        list_response = await client.get(
            "/api/v1/plans"
        )

        assert (
            list_response.status_code == 200
        ), list_response.text

        cached = await redis_client.get(
            "plans:active"
        )

        assert cached is not None

        cached_plans = json.loads(cached)

        assert len(cached_plans) == 1
        assert cached_plans[0]["name"] == "Pro"

        plan_id = create_response.json()["id"]

        update_response = await client.patch(
            f"/api/v1/admin/plans/{plan_id}",
            headers=headers,
            json={
                "name": "Pro Plus",
            },
        )

        assert (
            update_response.status_code == 200
        ), update_response.text

        assert (
            await redis_client.get(
                "plans:active"
            )
            is None
        )

        refreshed_response = await client.get(
            "/api/v1/plans"
        )

        assert (
            refreshed_response.status_code == 200
        ), refreshed_response.text

        assert (
            refreshed_response.json()[0]["name"]
            == "Pro Plus"
        )
