from sqlalchemy.orm import Session

from app.models.context import ContextItem
from app.models.context_links import (
    EventContext,
    ReminderContext,
    TaskContext,
)
from app.models.event import Event
from app.models.reminder import Reminder
from app.models.task import Task


def get_task_context(
    db: Session,
    task: Task,
) -> list[ContextItem]:
    return (
        db.query(ContextItem)
        .join(
            TaskContext,
            TaskContext.context_id == ContextItem.id,
        )
        .filter(
            TaskContext.task_id == task.id,
            ContextItem.user_id == task.user_id,
        )
        .order_by(ContextItem.created_at.desc())
        .all()
    )


def get_event_context(
    db: Session,
    event: Event,
) -> list[ContextItem]:
    return (
        db.query(ContextItem)
        .join(
            EventContext,
            EventContext.context_id == ContextItem.id,
        )
        .filter(
            EventContext.event_id == event.id,
            ContextItem.user_id == event.user_id,
        )
        .order_by(ContextItem.created_at.desc())
        .all()
    )


def get_reminder_context(
    db: Session,
    reminder: Reminder,
) -> list[ContextItem]:
    return (
        db.query(ContextItem)
        .join(
            ReminderContext,
            ReminderContext.context_id == ContextItem.id,
        )
        .filter(
            ReminderContext.reminder_id == reminder.id,
            ContextItem.user_id == reminder.user_id,
        )
        .order_by(ContextItem.created_at.desc())
        .all()
    )