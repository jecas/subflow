from __future__ import annotations

from typing import TYPE_CHECKING

from enum import StrEnum

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.subscription import Subscription


class CustomerRole(StrEnum):
    CUSTOMER = "customer"
    ADMIN = "admin"


class Customer(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "customers"

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    role: Mapped[CustomerRole] = mapped_column(
        Enum(CustomerRole),
        default=CustomerRole.CUSTOMER,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    subscriptions: Mapped[list["Subscription"]] = relationship(
        back_populates="customer",
    )
