from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.time import utc_now
from app.db.base import Base


class ContextItem(Base):
    __tablename__ = "context_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
    )

    context_type: Mapped[str] = mapped_column(
        String(50),
    )

    title: Mapped[str] = mapped_column(
        String(200),
    )

    value: Mapped[str] = mapped_column(
        Text,
    )

    source: Mapped[str] = mapped_column(
        String(30),
        default="manual",
    )

    extra_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )