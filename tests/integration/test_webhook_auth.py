import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.main import app


@pytest.mark.asyncio
async def test_webhook_requires_secret() -> None:
    transport = ASGITransport(
        app=app
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/webhooks/payments",
            json={
                "event_id": "evt_no_secret",
                "event_type": "payment.failed",
                "payment_id": "payment_1",
            },
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_webhook_rejects_invalid_secret() -> None:
    transport = ASGITransport(
        app=app
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/webhooks/payments",
            headers={
                "X-Webhook-Secret": "wrong-secret",
            },
            json={
                "event_id": "evt_wrong_secret",
                "event_type": "payment.failed",
                "payment_id": "payment_1",
            },
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_webhook_accepts_valid_secret() -> None:
    settings = get_settings()

    transport = ASGITransport(
        app=app
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/webhooks/payments",
            headers={
                "X-Webhook-Secret": (
                    settings.payment_webhook_secret
                ),
            },
            json={
                "event_id": "evt_valid_secret",
                "event_type": "payment.failed",
                "payment_id": "missing_payment",
            },
        )

    assert response.status_code == 200

    assert response.json() == {
        "event_id": "evt_valid_secret",
        "processed": True,
        "duplicate": False,
    }
