from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol
from uuid import uuid4


@dataclass(frozen=True)
class PaymentResult:
    provider_payment_id: str
    succeeded: bool


class PaymentProvider(Protocol):
    async def charge(
        self,
        *,
        amount: Decimal,
        currency: str,
        idempotency_key: str,
    ) -> PaymentResult: ...


class MockPaymentProvider:
    async def charge(
        self,
        *,
        amount: Decimal,
        currency: str,
        idempotency_key: str,
    ) -> PaymentResult:
        del amount, currency
        return PaymentResult(
            provider_payment_id=f"mock_{idempotency_key}_{uuid4().hex[:8]}",
            succeeded=True,
        )
