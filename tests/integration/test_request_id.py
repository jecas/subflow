import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_request_id_is_returned() -> None:
    transport = ASGITransport(
        app=app
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/health",
            headers={
                "X-Request-ID": "request-123"
            },
        )

    assert response.status_code == 200

    assert (
        response.headers["X-Request-ID"]
        == "request-123"
    )
