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
