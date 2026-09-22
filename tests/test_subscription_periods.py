from datetime import UTC, datetime

from app.models.plan import BillingPeriod
from app.services.subscription import _next_period


def test_monthly_period_is_calendar_aware() -> None:
    start = datetime(2026, 1, 31, tzinfo=UTC)

    result = _next_period(start, BillingPeriod.MONTHLY)

    assert result == datetime(2026, 2, 28, tzinfo=UTC)


def test_yearly_period_is_calendar_aware() -> None:
    start = datetime(2024, 2, 29, tzinfo=UTC)

    result = _next_period(start, BillingPeriod.YEARLY)

    assert result == datetime(2025, 2, 28, tzinfo=UTC)
