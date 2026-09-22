"""Initial schema.

Revision ID: 0001
Revises:
Create Date: 2026-09-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    customer_role = postgresql.ENUM(
        "CUSTOMER",
        "ADMIN",
        name="customerrole",
        create_type=False,
    )

    billing_period = postgresql.ENUM(
        "MONTHLY",
        "YEARLY",
        name="billingperiod",
        create_type=False,
    )

    subscription_status = postgresql.ENUM(
        "ACTIVE",
        "CANCELED",
        "EXPIRED",
        name="subscriptionstatus",
        create_type=False,
    )

    customer_role.create(op.get_bind(), checkfirst=True)
    billing_period.create(op.get_bind(), checkfirst=True)
    subscription_status.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.create_table(
        "customers",
        sa.Column(
            "email",
            sa.String(length=320),
            nullable=False,
        ),
        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "first_name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "last_name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "role",
            customer_role,
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_customers_email"),
        "customers",
        ["email"],
        unique=True,
    )

    op.create_table(
        "plans",
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "price",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
        ),
        sa.Column(
            "currency",
            sa.String(length=3),
            nullable=False,
        ),
        sa.Column(
            "billing_period",
            billing_period,
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "subscriptions",
        sa.Column(
            "customer_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "plan_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "status",
            subscription_status,
            nullable=False,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "current_period_end",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "cancel_at_period_end",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["plan_id"],
            ["plans.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_subscriptions_customer_id"),
        "subscriptions",
        ["customer_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_subscriptions_plan_id"),
        "subscriptions",
        ["plan_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_subscriptions_plan_id"),
        table_name="subscriptions",
    )

    op.drop_index(
        op.f("ix_subscriptions_customer_id"),
        table_name="subscriptions",
    )

    op.drop_table("subscriptions")
    op.drop_table("plans")

    op.drop_index(
        op.f("ix_customers_email"),
        table_name="customers",
    )

    op.drop_table("customers")

    postgresql.ENUM(
        name="subscriptionstatus",
    ).drop(
        op.get_bind(),
        checkfirst=True,
    )

    postgresql.ENUM(
        name="billingperiod",
    ).drop(
        op.get_bind(),
        checkfirst=True,
    )

    postgresql.ENUM(
        name="customerrole",
    ).drop(
        op.get_bind(),
        checkfirst=True,
    )
