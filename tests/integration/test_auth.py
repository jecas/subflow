import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_protected_endpoint_requires_authentication() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/api/v1/customers/me"
        )

    assert response.status_code == 401, response.text
    assert response.json() == {
        "error": {
            "code": "authentication_error",
            "message": (
                "Authentication credentials "
                "are required."
            ),
        }
    }


@pytest.mark.asyncio
async def test_invalid_token_is_rejected() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/api/v1/customers/me",
            headers={
                "Authorization": "Bearer invalid-token"
            },
        )

    assert response.status_code == 401, response.text
    assert response.json() == {
        "error": {
            "code": "authentication_error",
            "message": "Invalid or expired access token.",
        }
    }

@pytest.mark.asyncio
async def test_customer_cannot_access_admin_endpoint() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "customer@example.com",
                "password": "StrongPassword123!",
                "first_name": "Regular",
                "last_name": "Customer",
            },
        )

        assert (
            register_response.status_code == 201
        ), register_response.text

        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "customer@example.com",
                "password": "StrongPassword123!",
            },
        )

        assert (
            login_response.status_code == 200
        ), login_response.text

        token = login_response.json()[
            "access_token"
        ]

        response = await client.get(
            "/api/v1/admin/customers",
            headers={
                "Authorization": f"Bearer {token}"
            },
        )

    assert response.status_code == 403, response.text
    assert response.json() == {
        "error": {
            "code": "authorization_error",
            "message": (
                "Administrator access is required."
            ),
        }
    }
