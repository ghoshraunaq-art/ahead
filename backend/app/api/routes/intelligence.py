from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.event import Event
from app.models.reminder import Reminder
from app.models.task import Task
from app.schemas.context_intelligence import ContextIntelligenceResponse
from app.services.context_intelligence import (
    get_event_context,
    get_reminder_context,
    get_task_context,
)


router = APIRouter(
    prefix="/intelligence",
    tags=["intelligence"],
)


# Temporary development user.
# This will be replaced by real authentication later.
DEVELOPMENT_USER_ID = 1


@router.get(
    "/tasks/{task_id}/context",
    response_model=ContextIntelligenceResponse,
)
def get_task_intelligence(
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

    context_items = get_task_context(
        db=db,
        task=task,
    )

    return ContextIntelligenceResponse(
        entity_type="task",
        entity_id=task.id,
        context=[
            {
                "id": item.id,
                "context_type": item.context_type,
                "title": item.title,
                "value": item.value,
                "source": item.source,
                "extra_data": item.extra_data,
            }
            for item in context_items
        ],
    )


@router.get(
    "/events/{event_id}/context",
    response_model=ContextIntelligenceResponse,
)
def get_event_intelligence(
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

    context_items = get_event_context(
        db=db,
        event=event,
    )

    return ContextIntelligenceResponse(
        entity_type="event",
        entity_id=event.id,
        context=[
            {
                "id": item.id,
                "context_type": item.context_type,
                "title": item.title,
                "value": item.value,
                "source": item.source,
                "extra_data": item.extra_data,
            }
            for item in context_items
        ],
    )


@router.get(
    "/reminders/{reminder_id}/context",
    response_model=ContextIntelligenceResponse,
)
def get_reminder_intelligence(
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

    context_items = get_reminder_context(
        db=db,
        reminder=reminder,
    )

    return ContextIntelligenceResponse(
        entity_type="reminder",
        entity_id=reminder.id,
        context=[
            {
                "id": item.id,
                "context_type": item.context_type,
                "title": item.title,
                "value": item.value,
                "source": item.source,
                "extra_data": item.extra_data,
            }
            for item in context_items
        ],
    )