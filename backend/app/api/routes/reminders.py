from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.reminder import Reminder
from app.schemas.reminder import (
    ReminderCreate,
    ReminderResponse,
    ReminderUpdate,
)

router = APIRouter(
    prefix="/reminders",
    tags=["reminders"],
)


# Temporary development user.
# This will be replaced by real authentication later.
DEVELOPMENT_USER_ID = 1


@router.post("/", response_model=ReminderResponse)
def create_reminder(
    reminder_data: ReminderCreate,
    db: Session = Depends(get_db),
):
    reminder = Reminder(
        user_id=DEVELOPMENT_USER_ID,
        title=reminder_data.title,
        message=reminder_data.message,
        remind_at=reminder_data.remind_at,
        status=reminder_data.status,
    )

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    return reminder


@router.get("/", response_model=list[ReminderResponse])
def get_reminders(
    db: Session = Depends(get_db),
):
    return (
        db.query(Reminder)
        .filter(Reminder.user_id == DEVELOPMENT_USER_ID)
        .order_by(Reminder.remind_at)
        .all()
    )


@router.get("/{reminder_id}", response_model=ReminderResponse)
def get_reminder(
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

    return reminder


@router.patch("/{reminder_id}", response_model=ReminderResponse)
def update_reminder(
    reminder_id: int,
    reminder_data: ReminderUpdate,
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

    update_data = reminder_data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(reminder, field, value)

    db.commit()
    db.refresh(reminder)

    return reminder


@router.delete("/{reminder_id}")
def delete_reminder(
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

    db.delete(reminder)
    db.commit()

    return {
        "message": "Reminder deleted successfully",
    }