from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TaskContext(Base):
    __tablename__ = "task_contexts"

    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    )

    context_id: Mapped[int] = mapped_column(
        ForeignKey("context_items.id", ondelete="CASCADE"),
        primary_key=True,
    )


class EventContext(Base):
    __tablename__ = "event_contexts"

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"),
        primary_key=True,
    )

    context_id: Mapped[int] = mapped_column(
        ForeignKey("context_items.id", ondelete="CASCADE"),
        primary_key=True,
    )


class ReminderContext(Base):
    __tablename__ = "reminder_contexts"

    reminder_id: Mapped[int] = mapped_column(
        ForeignKey("reminders.id", ondelete="CASCADE"),
        primary_key=True,
    )

    context_id: Mapped[int] = mapped_column(
        ForeignKey("context_items.id", ondelete="CASCADE"),
        primary_key=True,
    )