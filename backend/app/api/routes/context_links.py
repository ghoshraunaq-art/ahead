from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.context import ContextItem
from app.models.context_links import (
    EventContext,
    ReminderContext,
    TaskContext,
)
from app.models.event import Event
from app.models.reminder import Reminder
from app.models.task import Task
from app.schemas.context import ContextResponse


router = APIRouter(
    tags=["context-links"],
)


# Temporary development user.
# This will be replaced by real authentication later.
DEVELOPMENT_USER_ID = 1


@router.post(
    "/tasks/{task_id}/context/{context_id}",
    response_model=ContextResponse,
)
def attach_context_to_task(
    task_id: int,
    context_id: int,
    db: Session = Depends(get_db),
):
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == DEVELOPMENT_USER_ID,
        )
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    context_item = (
        db.query(ContextItem)
        .filter(
            ContextItem.id == context_id,
            ContextItem.user_id == DEVELOPMENT_USER_ID,
        )
        .first()
    )

    if context_item is None:
        raise HTTPException(
            status_code=404,
            detail="Context item not found",
        )

    existing_link = (
        db.query(TaskContext)
        .filter(
            TaskContext.task_id == task_id,
            TaskContext.context_id == context_id,
        )
        .first()
    )

    if existing_link is not None:
        raise HTTPException(
            status_code=409,
            detail="Context is already attached to this task",
        )

    db.add(
        TaskContext(
            task_id=task_id,
            context_id=context_id,
        )
    )
    db.commit()

    return context_item


@router.get(
    "/tasks/{task_id}/context",
    response_model=list[ContextResponse],
)
def get_task_context(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == DEVELOPMENT_USER_ID,
        )
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return (
        db.query(ContextItem)
        .join(
            TaskContext,
            TaskContext.context_id == ContextItem.id,
        )
        .filter(
            TaskContext.task_id == task_id,
            ContextItem.user_id == DEVELOPMENT_USER_ID,
        )
        .order_by(ContextItem.created_at.desc())
        .all()
    )


@router.delete(
    "/tasks/{task_id}/context/{context_id}",
)
def detach_context_from_task(
    task_id: int,
    context_id: int,
    db: Session = Depends(get_db),
):
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == DEVELOPMENT_USER_ID,
        )
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    link = (
        db.query(TaskContext)
        .filter(
            TaskContext.task_id == task_id,
            TaskContext.context_id == context_id,
        )
        .first()
    )

    if link is None:
        raise HTTPException(
            status_code=404,
            detail="Context is not attached to this task",
        )

    db.delete(link)
    db.commit()

    return {
        "message": "Context detached from task successfully",
    }


@router.post(
    "/events/{event_id}/context/{context_id}",
    response_model=ContextResponse,
)
def attach_context_to_event(
    event_id: int,
    context_id: int,
    db: Session = Depends(get_db),
):
    event = (
        db.query(Event)
        .filter(
            Event.id == event_id,
            Event.user_id == DEVELOPMENT_USER_ID,
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found",
        )

    context_item = (
        db.query(ContextItem)
        .filter(
            ContextItem.id == context_id,
            ContextItem.user_id == DEVELOPMENT_USER_ID,
        )
        .first()
    )

    if context_item is None:
        raise HTTPException(
            status_code=404,
            detail="Context item not found",
        )

    existing_link = (
        db.query(EventContext)
        .filter(
            EventContext.event_id == event_id,
            EventContext.context_id == context_id,
        )
        .first()
    )

    if existing_link is not None:
        raise HTTPException(
            status_code=409,
            detail="Context is already attached to this event",
        )

    db.add(
        EventContext(
            event_id=event_id,
            context_id=context_id,
        )
    )
    db.commit()

    return context_item


@router.get(
    "/events/{event_id}/context",
    response_model=list[ContextResponse],
)
def get_event_context(
    event_id: int,
    db: Session = Depends(get_db),
):
    event = (
        db.query(Event)
        .filter(
            Event.id == event_id,
            Event.user_id == DEVELOPMENT_USER_ID,
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found",
        )

    return (
        db.query(ContextItem)
        .join(
            EventContext,
            EventContext.context_id == ContextItem.id,
        )
        .filter(
            EventContext.event_id == event_id,
            ContextItem.user_id == DEVELOPMENT_USER_ID,
        )
        .order_by(ContextItem.created_at.desc())
        .all()
    )


@router.delete(
    "/events/{event_id}/context/{context_id}",
)
def detach_context_from_event(
    event_id: int,
    context_id: int,
    db: Session = Depends(get_db),
):
    event = (
        db.query(Event)
        .filter(
            Event.id == event_id,
            Event.user_id == DEVELOPMENT_USER_ID,
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found",
        )

    link = (
        db.query(EventContext)
        .filter(
            EventContext.event_id == event_id,
            EventContext.context_id == context_id,
        )
        .first()
    )

    if link is None:
        raise HTTPException(
            status_code=404,
            detail="Context is not attached to this event",
        )

    db.delete(link)
    db.commit()

    return {
        "message": "Context detached from event successfully",
    }


@router.post(
    "/reminders/{reminder_id}/context/{context_id}",
    response_model=ContextResponse,
)
def attach_context_to_reminder(
    reminder_id: int,
    context_id: int,
    db: Session = Depends(get_db),
):
    reminder = (
        db.query(Reminder)
        .filter(
            Reminder.id == reminder_id,
            Reminder.user_id == DEVELOPMENT_USER_ID,
        )
        .first()
    )

    if reminder is None:
        raise HTTPException(
            status_code=404,
            detail="Reminder not found",
        )

    context_item = (
        db.query(ContextItem)
        .filter(
            ContextItem.id == context_id,
            ContextItem.user_id == DEVELOPMENT_USER_ID,
        )
        .first()
    )

    if context_item is None:
        raise HTTPException(
            status_code=404,
            detail="Context item not found",
        )

    existing_link = (
        db.query(ReminderContext)
        .filter(
            ReminderContext.reminder_id == reminder_id,
            ReminderContext.context_id == context_id,
        )
        .first()
    )

    if existing_link is not None:
        raise HTTPException(
            status_code=409,
            detail="Context is already attached to this reminder",
        )

    db.add(
        ReminderContext(
            reminder_id=reminder_id,
            context_id=context_id,
        )
    )
    db.commit()

    return context_item


@router.get(
    "/reminders/{reminder_id}/context",
    response_model=list[ContextResponse],
)
def get_reminder_context(
    reminder_id: int,
    db: Session = Depends(get_db),
):
    reminder = (
        db.query(Reminder)
        .filter(
            Reminder.id == reminder_id,
            Reminder.user_id == DEVELOPMENT_USER_ID,
        )
        .first()
    )

    if reminder is None:
        raise HTTPException(
            status_code=404,
            detail="Reminder not found",
        )

    return (
        db.query(ContextItem)
        .join(
            ReminderContext,
            ReminderContext.context_id == ContextItem.id,
        )
        .filter(
            ReminderContext.reminder_id == reminder_id,
            ContextItem.user_id == DEVELOPMENT_USER_ID,
        )
        .order_by(ContextItem.created_at.desc())
        .all()
    )


@router.delete(
    "/reminders/{reminder_id}/context/{context_id}",
)
def detach_context_from_reminder(
    reminder_id: int,
    context_id: int,
    db: Session = Depends(get_db),
):
    reminder = (
        db.query(Reminder)
        .filter(
            Reminder.id == reminder_id,
            Reminder.user_id == DEVELOPMENT_USER_ID,
        )
        .first()
    )

    if reminder is None:
        raise HTTPException(
            status_code=404,
            detail="Reminder not found",
        )

    link = (
        db.query(ReminderContext)
        .filter(
            ReminderContext.reminder_id == reminder_id,
            ReminderContext.context_id == context_id,
        )
        .first()
    )

    if link is None:
        raise HTTPException(
            status_code=404,
            detail="Context is not attached to this reminder",
        )

    db.delete(link)
    db.commit()

    return {
        "message": "Context detached from reminder successfully",
    }