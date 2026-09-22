from decimal import Decimal

import pytest

from app.providers.payment import MockPaymentProvider


@pytest.mark.asyncio
async def test_mock_payment_provider_succeeds() -> None:
    result = await MockPaymentProvider().charge(
        amount=Decimal("29.99"),
        currency="EUR",
        idempotency_key="test-payment",
    )

    assert result.succeeded is True

    assert result.provider_payment_id.startswith(
        "mock_test-payment_"
    )
