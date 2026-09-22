"""Add payment idempotency key.

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-22
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "payments",
        sa.Column(
            "idempotency_key",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE payments
        SET idempotency_key = 'legacy_' || id::text
        WHERE idempotency_key IS NULL
        """
    )

    op.alter_column(
        "payments",
        "idempotency_key",
        existing_type=sa.String(length=255),
        nullable=False,
    )

    op.create_index(
        op.f("ix_payments_idempotency_key"),
        "payments",
        ["idempotency_key"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_payments_idempotency_key"),
        table_name="payments",
    )

    op.drop_column(
        "payments",
        "idempotency_key",
    )
