from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.event import Event
from app.schemas.event import EventCreate, EventResponse, EventUpdate

router = APIRouter(
    prefix="/events",
    tags=["events"],
)


# Temporary development user.
# This will be replaced by real authentication later.
DEVELOPMENT_USER_ID = 1


@router.post("/", response_model=EventResponse)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
):
    event = Event(
        user_id=DEVELOPMENT_USER_ID,
        title=event_data.title,
        description=event_data.description,
        starts_at=event_data.starts_at,
        ends_at=event_data.ends_at,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@router.get("/", response_model=list[EventResponse])
def get_events(
    db: Session = Depends(get_db),
):
    return (
        db.query(Event)
        .filter(Event.user_id == DEVELOPMENT_USER_ID)
        .order_by(Event.starts_at)
        .all()
    )


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
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

    return event


@router.patch("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_data: EventUpdate,
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

    update_data = event_data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)

    return event


@router.delete("/{event_id}")
def delete_event(
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

    db.delete(event)
    db.commit()

    return {
        "message": "Event deleted successfully",
    }